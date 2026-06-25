"""
Schedule Agent — official convention schedule lookups and conflict checks.

All data comes exclusively from ``EventDataAPI``.  The agent never invents
or guesses times/locations; if data is TBD, it says so explicitly.
"""

from google.adk import Agent
from event_data_api import EventDataAPI


# ── tool functions ──────────────────────────────────────────────────────

def get_full_schedule() -> dict:
    """Return the complete convention schedule from the official EventDataAPI."""
    return EventDataAPI.get_schedule()


def get_panel_info(panel_name: str) -> dict:
    """Look up a single panel by *panel_name* and return its details with provenance.

    Returns a dict with panel details if found, or an error dict with
    ``source`` attribution when the panel cannot be located.
    """
    info = EventDataAPI.get_panel_info(panel_name)
    if info is None:
        return {"error": "Panel not found in official data", "source": "EventDataAPI"}
    # Attach provenance tag to the result
    if isinstance(info, dict):
        info["source"] = "EventDataAPI"
    return info


def check_schedule_conflicts(event_a: str, event_b: str) -> dict:
    """Check whether two events overlap in time.

    Looks up both panels via ``EventDataAPI.get_panel_info`` and compares
    their start/end times.  Returns a dict describing the conflict status.
    """
    panel_a = EventDataAPI.get_panel_info(event_a)
    panel_b = EventDataAPI.get_panel_info(event_b)

    if panel_a is None:
        return {"error": f"Panel '{event_a}' not found in official data", "source": "EventDataAPI"}
    if panel_b is None:
        return {"error": f"Panel '{event_b}' not found in official data", "source": "EventDataAPI"}

    # Extract time fields (implementation depends on EventDataAPI schema)
    start_a = panel_a.get("start_time")
    end_a = panel_a.get("end_time")
    start_b = panel_b.get("start_time")
    end_b = panel_b.get("end_time")

    # If any time is TBD / missing, we cannot determine a conflict
    if None in (start_a, end_a, start_b, end_b):
        return {
            "conflict": "unknown",
            "reason": "One or both panels have TBD times — cannot determine overlap.",
            "event_a": event_a,
            "event_b": event_b,
            "source": "EventDataAPI",
        }

    # Simple overlap check: A starts before B ends AND B starts before A ends
    has_conflict = start_a < end_b and start_b < end_a

    return {
        "conflict": has_conflict,
        "event_a": {"name": event_a, "start": start_a, "end": end_a},
        "event_b": {"name": event_b, "start": start_b, "end": end_b},
        "source": "EventDataAPI",
    }


# ── agent instance ──────────────────────────────────────────────────────

schedule_agent = Agent(
    name="schedule_agent",
    instruction=(
        "You manage the convention schedule. Only use data from the official "
        "EventDataAPI. Never invent or guess times/locations. If data shows "
        "'TBD', say so clearly. Tag every fact as 'confirmed via official "
        "event data'."
    ),
    tools=[
        get_full_schedule,
        get_panel_info,
        check_schedule_conflicts,
    ],
)
