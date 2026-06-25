"""
Weather Specialist Agent (STUB).

No live weather API is currently connected.  The single tool returns a
clear disclaimer directing users to weather.gov or the convention's
official app.  The venue location is pulled from EventDataAPI metadata
so the message is at least context-aware.
"""

from google.adk import Agent
from event_data_api import EventDataAPI


# ── Tool functions ───────────────────────────────────────────────────────────


def get_weather_forecast() -> str:
    """Return a disclaimer that no verified weather data is available.

    Pulls the venue location from EventDataAPI metadata so the response
    is contextually relevant even without a real weather feed.

    Returns:
        A string directing the user to official weather sources.
    """
    location = EventDataAPI.get_metadata().get("location", "the venue")
    return (
        f"No verified weather forecast available. "
        f"Please check weather.gov or the convention official app "
        f"for current conditions at {location}."
    )


# ── Agent definition ─────────────────────────────────────────────────────────

weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="Specialist for weather information (currently a stub with no live data).",
    instruction=(
        "You provide weather information. "
        "Currently no live weather API is connected. "
        "Always clearly state that weather data is not verified "
        "and direct users to official sources like weather.gov."
    ),
    tools=[get_weather_forecast],
)
