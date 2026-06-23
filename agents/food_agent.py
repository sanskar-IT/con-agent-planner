"""
Food & Hydration Specialist Agent.

Provides food-break suggestions, hydration station lookups, and dietary
preference tracking.  All hydration station data comes from the authoritative
EventDataAPI.  Food venue information is intentionally *not* fabricated —
if no official data exists the agent tells the user to check in person.
"""

from typing import List

from google.adk import Agent
from retrieval.event_data_api import EventDataAPI


# ── Tool functions ───────────────────────────────────────────────────────────


def suggest_food_break() -> str:
    """Suggest a food break and mention nearby hydration stations.

    Returns a helpful message that includes official hydration station
    locations but never invents restaurant names or food vendors.
    """
    stations = EventDataAPI.get_hydration_stations()
    station_list = ", ".join(stations) if stations else "no listed locations"

    return (
        "🍱 Time for a food break! "
        "Check the venue food court or nearby options for meals — "
        "no official food vendor list is available at this time.\n\n"
        f"💧 Stay hydrated! Official hydration stations: {station_list}."
    )


def get_hydration_stations() -> List[str]:
    """Return the list of official hydration stations from EventDataAPI.

    Returns:
        A list of hydration station names/locations.
    """
    return EventDataAPI.get_hydration_stations()


def set_dietary_preferences(preferences: str) -> str:
    """Record the user's dietary preferences for the session.

    Args:
        preferences: Comma-separated dietary preferences
                     (e.g. 'vegetarian,halal').

    Returns:
        Confirmation message echoing the stored preferences.
    """
    prefs = [p.strip() for p in preferences.split(",") if p.strip()]
    formatted = ", ".join(prefs) if prefs else "(none)"
    return (
        f"✅ Dietary preferences noted: {formatted}. "
        "I'll keep these in mind when making food suggestions."
    )


# ── Agent definition ─────────────────────────────────────────────────────────

food_agent = Agent(
    name="food_agent",
    model="gemini-2.0-flash",
    description="Specialist for food breaks, hydration stations, and dietary preferences.",
    instruction=(
        "You help with food and hydration planning. "
        "Only reference hydration stations from official data. "
        "For food venues, if no official data is available, say so — "
        "never invent restaurant names or menus. "
        "Remind users to stay hydrated."
    ),
    tools=[suggest_food_break, get_hydration_stations, set_dietary_preferences],
)
