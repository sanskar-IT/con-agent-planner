"""
Runner — sends messages to the Jarvis convention assistant.

Provides both sync and async interfaces for sending messages to the
ADK agent.  Emergency bypass is now handled by the emergency_agent
sub-agent, but we keep a pre-flight check here for instant deterministic
responses on safety-critical queries (no round-trip to LLM).
"""

import asyncio
from google.adk import Runner
from google.genai import types
from google.adk.sessions import InMemorySessionService
from agent import root_agent
from agents.emergency_agent import check_emergency


_session_service = InMemorySessionService()


async def send_to_agent(session_id: str, text: str) -> str:
    """Send a message to the Jarvis assistant and return the response.

    The emergency pre-flight check runs first for instant deterministic
    responses. Otherwise, the message flows through the full ADK runner.
    """
    # Pre-flight emergency check — bypass LLM for safety queries
    emergency_response = check_emergency(text)
    if emergency_response:
        return emergency_response

    new_message = types.UserContent(parts=[types.Part.from_text(text=text)])

    runner = Runner(
        agent=root_agent,
        session_service=_session_service,
        app_name="jarvis_convention_assistant",
        auto_create_session=True,
    )

    response_content = ""
    async for event in runner.run_async(
        user_id=session_id,
        session_id=session_id,
        new_message=new_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                response_content += event.content.parts[0].text

    return response_content


def run(session_id: str, text: str) -> str:
    """Synchronous wrapper for send_to_agent."""
    return asyncio.run(send_to_agent(session_id, text))


def run_with_state(session_id: str, text: str):
    """Run a query and also return the updated convention state.

    Returns:
        Tuple of (response_text, state_summary_dict).
    """
    from session_service import ConventionSessionService

    response = run(session_id, text)
    session_svc = ConventionSessionService()
    state_summary = session_svc.get_state_summary(session_id)
    return response, state_summary
