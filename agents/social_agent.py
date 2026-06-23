"""
Social Agent — official announcements and community update monitor.

Strictly separates verified official announcements from community /
social-media updates.  Every community item carries a ``confidence_label``
so the user can gauge reliability.
"""

from google.adk import Agent
from retrieval.rag_retriever import RAGRetriever


# ── tool functions ──────────────────────────────────────────────────────

def get_official_announcements() -> list:
    """Return only verified official announcements from the RAG store."""
    return RAGRetriever.get_verified_only()


def get_community_updates() -> list:
    """Return community / social-media updates.

    Each item in the returned list includes a ``confidence_label``
    indicating the reliability tier of the source.
    """
    return RAGRetriever.get_community_updates()


def search_updates(query: str) -> list:
    """Search all updates (official + community) for *query*.

    Results are filtered through the provenance pipeline
    (``apply_filtering=True``) so that each item carries source
    attribution and confidence metadata.
    """
    return RAGRetriever.query_with_provenance(query, apply_filtering=True)


# ── agent instance ──────────────────────────────────────────────────────

social_agent = Agent(
    name="social_agent",
    instruction=(
        "You monitor official announcements and community updates. ALWAYS "
        "distinguish between official and unofficial sources. Present "
        "official announcements first. For community/social updates, always "
        "include the confidence label (e.g., 'reported by unofficial "
        "source'). NEVER present speculation as fact."
    ),
    tools=[
        get_official_announcements,
        get_community_updates,
        search_updates,
    ],
)
