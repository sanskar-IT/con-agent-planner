"""
Verification Specialist Agent.

Classifies factual claims into trust tiers and tags each with a
confidence score using the ``verification.source_verifier`` module.
Provides a tool to explain what each tier means so users can assess
information quality on their own.
"""

from typing import Dict, Any

from google.adk import Agent
from verification.source_verifier import (
    SourceTier,
    SourceRecord,
    verify_claim,
    format_confidence_label,
)


# ── Tier detection helper ────────────────────────────────────────────────────


def _detect_tier(source_name: str) -> SourceTier:
    """Infer the appropriate SourceTier from a free-text source name.

    Matching rules (evaluated in order):
        1. Contains 'official' AND ('EventDataAPI' | 'press release')
           → OFFICIAL_ANNOUNCEMENT
        2. Contains ('twitter'|'x.com'|'instagram') AND 'official'
           → OFFICIAL_SOCIAL
        3. Contains ('reddit'|'twitter'|'instagram') without 'official'
           → UNOFFICIAL_SOCIAL
        4. Anything else → UNKNOWN
    """
    lower = source_name.lower()

    # Rule 1 — official announcements / API data
    if "official" in lower or "eventdataapi" in lower or "press release" in lower:
        # But if it's also social, it's official social (rule 2 takes precedence)
        social_keywords = ("twitter", "x.com", "instagram")
        if any(kw in lower for kw in social_keywords) and "official" in lower:
            return SourceTier.OFFICIAL_SOCIAL
        return SourceTier.OFFICIAL_ANNOUNCEMENT

    # Rule 3 — unofficial social
    social_keywords = ("reddit", "twitter", "instagram")
    if any(kw in lower for kw in social_keywords):
        return SourceTier.UNOFFICIAL_SOCIAL

    # Rule 4 — unknown
    return SourceTier.UNKNOWN


# ── Tool functions ───────────────────────────────────────────────────────────


def verify_fact(claim: str, source_name: str) -> Dict[str, Any]:
    """Verify a factual claim and return its trust classification.

    Determines the appropriate SourceTier from ``source_name``, runs
    ``verify_claim()``, and attaches a human-readable confidence label.

    Args:
        claim:       The factual statement to verify.
        source_name: Where the claim originated (e.g. 'official AX Twitter',
                     'reddit post', 'EventDataAPI').

    Returns:
        A dict containing the full SourceRecord fields plus a
        ``confidence_label`` string.
    """
    tier = _detect_tier(source_name)
    record: SourceRecord = verify_claim(
        claim=claim,
        source_name=source_name,
        tier=tier,
    )

    result = record.model_dump()
    result["confidence_label"] = format_confidence_label(record)
    return result


def get_source_summary() -> str:
    """Explain the trust-tier system to the user.

    Returns:
        A human-readable summary of each SourceTier and its meaning.
    """
    return (
        "📊 **Source Trust Tiers** (highest → lowest confidence):\n\n"
        "1. **OFFICIAL_API** (confidence 1.0) — Data from the authoritative "
        "event data system. Considered ground truth.\n"
        "2. **OFFICIAL_ANNOUNCEMENT** (confidence 0.95) — Press releases, "
        "official website posts, or verified announcements.\n"
        "3. **OFFICIAL_SOCIAL** (confidence 0.8) — Posts from verified "
        "official social-media accounts (e.g. @AX_Official on Twitter).\n"
        "4. **USER_PROVIDED** (confidence 0.5) — Information supplied "
        "directly by the user. Treated as plausible but unverified.\n"
        "5. **UNOFFICIAL_SOCIAL** (confidence 0.3) — Community posts on "
        "Reddit, Twitter fan accounts, Instagram, etc. May be inaccurate.\n"
        "6. **UNKNOWN** (confidence 0.0) — Source cannot be determined. "
        "Treat with extreme caution.\n\n"
        "⏳ *Stale data* (older than 1 hour) receives a 30% confidence penalty."
    )


# ── Agent definition ─────────────────────────────────────────────────────────

# Variable name is `verification_agent`; the Agent *name* is
# 'verification_specialist' to avoid collision with the module name.
verification_agent = Agent(
    name="verification_specialist",
    model="gemini-2.0-flash",
    description="Specialist for verifying factual claims and explaining source trust.",
    instruction=(
        "You verify factual claims. "
        "For every claim, determine the source tier and tag it with confidence. "
        "Explain to the user whether information is official, unofficial, or unverified. "
        "Never promote unverified claims to confirmed status."
    ),
    tools=[verify_fact, get_source_summary],
)
