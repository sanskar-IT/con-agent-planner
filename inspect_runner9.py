import asyncio
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService

agent = Agent(name="test_agent", model="gemini-3.5-flash", instruction="Say 'Hello world'.")
_session_service = InMemorySessionService()

async def main():
    try:
        runner = Runner(agent=agent, app_name="test_app", session_service=_session_service)
        print("Using run")
        res = runner.run("Hi", user_id="u1", session_id="s1")
        print("Res:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()
asyncio.run(main())
