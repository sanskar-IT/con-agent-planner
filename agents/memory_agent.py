"""
Memory & Preference Specialist Agent.

Tracks per-session user preferences, monitors energy levels, and
makes proactive wellbeing suggestions.  Hydration station data is
pulled from EventDataAPI so suggestions are grounded in real venue
information.
"""

from typing import Dict

from google.adk import Agent
from retrieval.event_data_api import EventDataAPI


# ── In-memory preference store (per-session) ─────────────────────────────────

_preferences: Dict[str, str] = {}


# ── Tool functions ───────────────────────────────────────────────────────────


def save_preference(key: str, value: str) -> str:
    """Save a user preference for the current session.

    Args:
        key:   Preference name (e.g. 'fav_genre', 'seating').
        value: Preference value.

    Returns:
        Confirmation that the preference was stored.
    """
    _preferences[key] = value
    return f"✅ Preference saved: {key} = {value}"


def get_preference(key: str) -> str:
    """Retrieve a previously saved preference.

    Args:
        key: The preference name to look up.

    Returns:
        The stored value, or a message indicating no preference is set.
    """
    value = _preferences.get(key)
    if value is not None:
        return value
    return f"No preference set for {key}"


def get_energy_suggestion(energy_level: int) -> str:
    """Return a wellbeing suggestion based on the user's self-reported energy.

    Energy scale: 1 (exhausted) → 10 (fully energised).

    Args:
        energy_level: Integer 1-10 representing current energy.

    Returns:
        Tailored suggestion including nearby hydration stations.
    """
    stations = EventDataAPI.get_hydration_stations()
    station_info = ", ".join(stations) if stations else "check venue signage"

    if energy_level <= 3:
        advice = (
            "⚠️ You seem very tired — consider taking an immediate rest break. "
            "Find a quiet spot, sit down, and recharge for at least 15 minutes."
        )
    elif energy_level <= 6:
        advice = (
            "😊 Energy is moderate — plan a break soon to avoid burnout. "
            "A short sit-down or snack can help you power through the rest of the day."
        )
    else:
        advice = (
            "💪 Energy is looking great! Keep enjoying the convention. "
            "Remember to schedule a break before you start feeling drained."
        )

    return f"{advice}\n\n💧 Hydration stations nearby: {station_info}."


def get_convention_summary() -> str:
    """Return a summary template the agent can populate with session data.

    Returns:
        A markdown-style summary template string.
    """
    saved = (
        "\n".join(f"  • {k}: {v}" for k, v in _preferences.items())
        if _preferences
        else "  (no preferences recorded yet)"
    )
    return (
        "📋 **Convention Day Summary**\n\n"
        "**Saved Preferences:**\n"
        f"{saved}\n\n"
        "**Sessions Attended:** (fill in from conversation history)\n\n"
        "**Key Highlights:** (fill in from conversation history)\n\n"
        "**Tomorrow's Plan:** (fill in based on remaining schedule)\n"
    )


# ── Agent definition ─────────────────────────────────────────────────────────

memory_agent = Agent(
    name="memory_agent",
    model="gemini-2.0-flash",
    description="Specialist for user preferences, energy tracking, and convention summaries.",
    instruction=(
        "You manage user preferences and memory. "
        "Track energy levels, past behavior, and recurring preferences. "
        "Make proactive suggestions based on energy "
        "(e.g., 'You seem tired — nearest hydration station is...'). "
        "Preferences are stored per-session."
    ),
    tools=[
        save_preference,
        get_preference,
        get_energy_suggestion,
        get_convention_summary,
    ],
)
