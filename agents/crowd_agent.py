"""
Crowd Estimation Specialist Agent (STUB).

No live crowd-density or queue-length feed is currently connected.
The tool acknowledges the gap and suggests practical alternatives
(social media, venue staff, visual inspection).
"""

from google.adk import Agent


# ── Tool functions ───────────────────────────────────────────────────────────


def get_crowd_estimate(location: str) -> str:
    """Return a disclaimer that crowd data is not available for the location.

    Args:
        location: The area or venue zone the user is asking about.

    Returns:
        A string explaining that no official crowd data exists and
        suggesting alternative ways to gauge conditions.
    """
    return (
        f"Crowd data for {location} is not available. "
        "No official queue or congestion estimates at this time. "
        "Check social media or ask venue staff for current conditions."
    )


# ── Agent definition ─────────────────────────────────────────────────────────

crowd_agent = Agent(
    name="crowd_agent",
    model="gemini-2.0-flash",
    description="Specialist for crowd condition estimates (currently a stub with no live data).",
    instruction=(
        "You estimate crowd conditions. "
        "Currently no live crowd data is available. "
        "Always clearly state that estimates are unavailable and suggest "
        "alternative ways to check (social media, venue staff, looking at queue length)."
    ),
    tools=[get_crowd_estimate],
)
