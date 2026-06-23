"""
Maps Agent — venue navigation and location lookup.

All spatial data comes from ``EventDataAPI`` and the underlying
``EVENT_DB['nav']`` structure.  The agent never guesses distances or
directions; if a location is missing from the map data it says so.
"""

from google.adk import Agent
from retrieval.event_data_api import EventDataAPI


# ── tool functions ──────────────────────────────────────────────────────

def get_location_coordinates(location_name: str) -> dict:
    """Return the (x, y) coordinates for *location_name* from the venue map.

    Returns a dict with coordinate data, or an error dict when the
    location is not found.
    """
    coords = EventDataAPI.get_coordinates(location_name)
    if coords is None:
        return {"error": "Location not found in venue map"}
    return coords


def list_exits() -> list:
    """Return a list of all venue exits from EventDataAPI."""
    return EventDataAPI.get_exits()


def list_first_aid() -> list:
    """Return a list of all first-aid station locations."""
    return EventDataAPI.get_first_aid()


def list_hydration_stations() -> list:
    """Return a list of all hydration / water stations."""
    return EventDataAPI.get_hydration_stations()


def get_venue_map_summary() -> dict:
    """Return a complete navigation summary for the venue.

    Aggregates exits, first-aid stations, hydration stations, and all
    known coordinates from ``EVENT_DB['nav']`` via ``EventDataAPI``.
    """
    return {
        "exits": EventDataAPI.get_exits(),
        "first_aid": EventDataAPI.get_first_aid(),
        "hydration_stations": EventDataAPI.get_hydration_stations(),
        "nav_data": EventDataAPI.get_nav(),
    }


# ── agent instance ──────────────────────────────────────────────────────

maps_agent = Agent(
    name="maps_agent",
    instruction=(
        "You provide venue navigation. Only use official coordinate and "
        "location data from EventDataAPI. Never guess distances or "
        "directions. If a location isn't in the map data, say so."
    ),
    tools=[
        get_location_coordinates,
        list_exits,
        list_first_aid,
        list_hydration_stations,
        get_venue_map_summary,
    ],
)
