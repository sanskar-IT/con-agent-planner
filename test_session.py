import asyncio
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

agent = Agent(name="test_agent", model="gemini-3.5-flash", instruction="Say 'Hello world'.")
_session_service = InMemorySessionService()

async def main():
    try:
        runner = Runner(agent=agent, app_name="test_app", session_service=_session_service)
        # Create session
        await _session_service.create_session(app_name="test_app", user_id="u1", session_id="s1")
        
        async for event in runner.run_async(user_id="u1", session_id="s1", new_message=types.UserContent(parts=[types.Part.from_text(text="Hi")])):
            if event.type == "output":
                print(event.data.text)
    except Exception as e:
        import traceback
        traceback.print_exc()
asyncio.run(main())
