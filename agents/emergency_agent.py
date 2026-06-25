"""
Emergency Agent — immediate triage routing for convention safety.

Promoted from the legacy runner.py emergency bypass.  Every response is
deterministic: keyword → resource lookup → formatted answer.  The canonical
response envelope is ``[EMERGENCY TRIAGE ROUTING] …`` so downstream
consumers can pattern-match on it.
"""

from google.adk import Agent
from event_data_api import EventDataAPI


# ── keyword list (order does not matter) ────────────────────────────────
EMERGENCY_KEYWORDS = [
    "emergency",
    "hurt",
    "exit",
    "water",
    "hydration",
    "panic",
    "first aid",
    "medical",
    "faint",
]


# ── tool functions ──────────────────────────────────────────────────────

def get_nearest_exit() -> str:
    """Return the nearest exit with its venue coordinates.

    Pulls the first entry from the official exit list and resolves its
    coordinates via EventDataAPI.
    """
    exits = EventDataAPI.get_exits()
    if not exits:
        return "No exit data available."
    nearest = exits[0]
    coords = EventDataAPI.get_coordinates(nearest)
    if coords:
        return f"Nearest exit: {nearest} (X={coords.get('x')}, Y={coords.get('y')})"
    return f"Nearest exit: {nearest} (coordinates unavailable)"


def get_nearest_first_aid() -> str:
    """Return the nearest first-aid station with its venue coordinates."""
    stations = EventDataAPI.get_first_aid()
    if not stations:
        return "No first-aid station data available."
    nearest = stations[0]
    coords = EventDataAPI.get_coordinates(nearest)
    if coords:
        return f"Nearest first aid: {nearest} (X={coords.get('x')}, Y={coords.get('y')})"
    return f"Nearest first aid: {nearest} (coordinates unavailable)"


def get_hydration_station() -> str:
    """Return the nearest hydration / water station with its venue coordinates."""
    stations = EventDataAPI.get_hydration_stations()
    if not stations:
        return "No hydration station data available."
    nearest = stations[0]
    coords = EventDataAPI.get_coordinates(nearest)
    if coords:
        return f"Nearest hydration station: {nearest} (X={coords.get('x')}, Y={coords.get('y')})"
    return f"Nearest hydration station: {nearest} (coordinates unavailable)"


def check_emergency(text: str) -> str:
    """Detect emergency keywords in *text* and return triage routing.

    Matching rules (first match wins):
    * ``exit``              → exit route
    * ``water`` / ``hydration`` → hydration station
    * any other keyword     → first-aid station

    Returns the canonical ``[EMERGENCY TRIAGE ROUTING] …`` string, or an
    empty string when no emergency keyword is found.
    """
    text_lower = text.lower()

    # Quick check: does the text contain any emergency keyword at all?
    if not any(kw in text_lower for kw in EMERGENCY_KEYWORDS):
        return ""

    # --- exit route ---
    if "exit" in text_lower:
        exits = EventDataAPI.get_exits()
        if exits:
            location = exits[0]
            coords = EventDataAPI.get_coordinates(location)
            if coords:
                x, y = coords.get("x"), coords.get("y")
                return (
                    f"[EMERGENCY TRIAGE ROUTING] Exit route requested. "
                    f"Nearest: {location} (X={x}, Y={y}). Head there now."
                )
            return (
                f"[EMERGENCY TRIAGE ROUTING] Exit route requested. "
                f"Nearest: {location}. Head there now."
            )
        return "[EMERGENCY TRIAGE ROUTING] Exit route requested. No exit data available."

    # --- hydration station ---
    if "water" in text_lower or "hydration" in text_lower:
        stations = EventDataAPI.get_hydration_stations()
        if stations:
            location = stations[0]
            coords = EventDataAPI.get_coordinates(location)
            if coords:
                x, y = coords.get("x"), coords.get("y")
                return (
                    f"[EMERGENCY TRIAGE ROUTING] Hydration requested. "
                    f"Nearest: {location} (X={x}, Y={y}). Head there now."
                )
            return (
                f"[EMERGENCY TRIAGE ROUTING] Hydration requested. "
                f"Nearest: {location}. Head there now."
            )
        return "[EMERGENCY TRIAGE ROUTING] Hydration requested. No station data available."

    # --- general medical / first aid ---
    stations = EventDataAPI.get_first_aid()
    if stations:
        location = stations[0]
        coords = EventDataAPI.get_coordinates(location)
        if coords:
            x, y = coords.get("x"), coords.get("y")
            return (
                f"[EMERGENCY TRIAGE ROUTING] Medical assistance requested. "
                f"Nearest: {location} (X={x}, Y={y}). Head there now."
            )
        return (
            f"[EMERGENCY TRIAGE ROUTING] Medical assistance requested. "
            f"Nearest: {location}. Head there now."
        )
    return "[EMERGENCY TRIAGE ROUTING] Medical assistance requested. No first-aid data available."


# ── agent instance ──────────────────────────────────────────────────────

emergency_agent = Agent(
    name="emergency_agent",
    instruction=(
        "You handle emergency situations at the convention. Always provide "
        "immediate, deterministic routing to safety resources. Never delay. "
        "Use get_nearest_exit for exit requests, get_hydration_station for "
        "water/hydration, get_nearest_first_aid for medical."
    ),
    tools=[
        get_nearest_exit,
        get_nearest_first_aid,
        get_hydration_station,
        check_emergency,
    ],
)
