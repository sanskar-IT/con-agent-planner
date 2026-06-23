"""
Source verification and provenance tagging.

Every factual claim in the system must pass through this module
to get a SourceRecord with a trust tier, confidence score, and
human-readable verification label.
"""

import time as time_module
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class SourceTier(str, Enum):
    """Trust tiers for information sources, ordered from most to least trusted."""
    OFFICIAL_API = "official_api"
    OFFICIAL_ANNOUNCEMENT = "official_announcement"
    OFFICIAL_SOCIAL = "official_social"
    UNOFFICIAL_SOCIAL = "unofficial_social"
    USER_PROVIDED = "user_provided"
    UNKNOWN = "unknown"


# Confidence scores assigned to each tier
TRUST_THRESHOLDS = {
    SourceTier.OFFICIAL_API: 1.0,
    SourceTier.OFFICIAL_ANNOUNCEMENT: 0.95,
    SourceTier.OFFICIAL_SOCIAL: 0.8,
    SourceTier.UNOFFICIAL_SOCIAL: 0.3,
    SourceTier.USER_PROVIDED: 0.5,
    SourceTier.UNKNOWN: 0.0,
}


class SourceRecord(BaseModel):
    """
    Provenance record for a single factual claim.

    Every piece of data surfaced to the user must be wrapped in a SourceRecord
    so the system can distinguish confirmed facts from speculation.
    """
    claim: str
    source_name: str
    tier: SourceTier
    timestamp: float
    is_stale: bool = False
    confidence: float = 0.0
    verified: bool = False


def verify_claim(
    claim: str,
    source_name: str,
    tier: SourceTier,
    timestamp: Optional[float] = None,
    stale_threshold_seconds: float = 3600.0,
) -> SourceRecord:
    """
    Create a SourceRecord for a claim with automatic confidence scoring.

    Args:
        claim: The factual claim being verified.
        source_name: Name of the data source (e.g., "EventDataAPI", "Twitter @AX_Official").
        tier: The trust tier of the source.
        timestamp: When the data was retrieved. Defaults to now.
        stale_threshold_seconds: How old data can be before it's marked stale.

    Returns:
        A SourceRecord with confidence and staleness computed.
    """
    now = time_module.time()
    ts = timestamp if timestamp is not None else now
    is_stale = (now - ts) > stale_threshold_seconds
    confidence = TRUST_THRESHOLDS.get(tier, 0.0)

    # Reduce confidence for stale data
    if is_stale:
        confidence *= 0.7

    verified = tier in (
        SourceTier.OFFICIAL_API,
        SourceTier.OFFICIAL_ANNOUNCEMENT,
    )

    return SourceRecord(
        claim=claim,
        source_name=source_name,
        tier=tier,
        timestamp=ts,
        is_stale=is_stale,
        confidence=confidence,
        verified=verified,
    )


def format_confidence_label(record: SourceRecord) -> str:
    """
    Return a human-readable verification label for a SourceRecord.

    Used in all agent output formatters to clearly communicate data trust.
    """
    if record.tier == SourceTier.OFFICIAL_API:
        return "confirmed via official event data"
    elif record.tier == SourceTier.OFFICIAL_ANNOUNCEMENT:
        return "confirmed via official announcement"
    elif record.tier == SourceTier.OFFICIAL_SOCIAL:
        return "confirmed via official social account"
    elif record.tier == SourceTier.UNOFFICIAL_SOCIAL:
        label = "reported by unofficial source"
        if record.is_stale:
            label += " (data may be stale)"
        return label
    elif record.tier == SourceTier.USER_PROVIDED:
        return "user-provided information"
    else:
        return "not verified — no reliable source found"


def is_trusted(record: SourceRecord) -> bool:
    """Return True if the record meets the minimum confidence threshold for display."""
    return record.confidence >= 0.5
