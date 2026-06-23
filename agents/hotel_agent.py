"""
Hotel & Lodging Specialist Agent.

Stores hotel details provided by the user and returns them on demand.
Commute estimates are explicitly marked as unavailable since no verified
transit data feed is connected — users are directed to Google Maps or
the convention shuttle schedule.
"""

from google.adk import Agent


# ── Tool functions ───────────────────────────────────────────────────────────


def set_hotel_info(name: str, address: str, checkin: str, checkout: str) -> str:
    """Store and confirm the user's hotel details.

    Args:
        name:     Hotel name (as provided by the user).
        address:  Hotel street address.
        checkin:  Check-in date/time string.
        checkout: Check-out date/time string.

    Returns:
        A nicely formatted confirmation of the stored hotel information.
    """
    return (
        "🏨 Hotel information saved!\n"
        f"  • Name:      {name}\n"
        f"  • Address:   {address}\n"
        f"  • Check-in:  {checkin}\n"
        f"  • Check-out: {checkout}\n\n"
        "I'll reference these details when helping you plan your days."
    )


def get_commute_estimate() -> str:
    """Return a disclaimer that commute estimates are not available.

    Returns:
        A string directing the user to Google Maps or the shuttle schedule.
    """
    return (
        "Commute estimate not available — no verified transit data. "
        "Please check Google Maps or the convention shuttle schedule "
        "for commute times."
    )


# ── Agent definition ─────────────────────────────────────────────────────────

hotel_agent = Agent(
    name="hotel_agent",
    model="gemini-2.0-flash",
    description="Specialist for lodging details and commute information.",
    instruction=(
        "You manage lodging information. "
        "Store hotel details provided by the user. "
        "For commute estimates, acknowledge that no verified transit data "
        "is available and suggest checking Google Maps. "
        "Never invent hotel names or addresses."
    ),
    tools=[set_hotel_info, get_commute_estimate],
)
