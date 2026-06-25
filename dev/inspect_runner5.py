import asyncio
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService

agent = Agent(name="test_agent", model="gemini-3.5-flash")

async def main():
    try:
        runner = Runner(agent=agent, app_name="test_app", session_service=InMemorySessionService())
        res = await runner.run_async("Hello")
        print(res.text)
    except Exception as e:
        import traceback
        traceback.print_exc()
asyncio.run(main())
