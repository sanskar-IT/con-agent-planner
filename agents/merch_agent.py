"""
Merch Agent — merchandise shopping assistant.

References only booths and items present in ``EventDataAPI``.  Never
invents vendor names, prices, or availability.  Helps prioritise
purchases within the user's remaining budget.
"""

from google.adk import Agent
from retrieval.event_data_api import EventDataAPI


# ── tool functions ──────────────────────────────────────────────────────

def list_booths() -> dict:
    """Return all vendor booths from the official EventDataAPI."""
    return EventDataAPI.get_booths()


def get_booth_details(booth_name: str) -> dict:
    """Look up a single booth by *booth_name*.

    Returns the booth's detail dict, or an error dict when the booth
    cannot be found in official data.
    """
    details = EventDataAPI.get_booth_by_name(booth_name)
    if details is None:
        return {"error": "Booth not found in official data"}
    return details


def get_booth_merchandise(booth_id: str) -> dict:
    """Return the merchandise listing for the booth identified by *booth_id*."""
    return EventDataAPI.get_booth_merchandise(booth_id)


def prioritize_merch_list(budget_remaining: float) -> str:
    """Provide guidance on prioritising merchandise within *budget_remaining*.

    This tool does **not** invent items.  It returns a message prompting
    the agent to rank already-known items against the remaining budget.
    """
    return (
        f"Budget remaining: ${budget_remaining:.2f}. "
        "Please review the merchandise items already retrieved from "
        "EventDataAPI and help the user prioritize purchases that fit "
        "within this budget. Do not invent any items or prices."
    )


# ── agent instance ──────────────────────────────────────────────────────

merch_agent = Agent(
    name="merch_agent",
    instruction=(
        "You help with merchandise shopping. Only reference booths and "
        "items from official EventDataAPI data. Never invent vendor names, "
        "prices, or availability. If booth data is empty, say 'no booth "
        "data available yet'. Help prioritize purchases within budget."
    ),
    tools=[
        list_booths,
        get_booth_details,
        get_booth_merchandise,
        prioritize_merch_list,
    ],
)
