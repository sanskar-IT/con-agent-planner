import asyncio
from google.adk import Agent, Runner
from google.adk.sessions import InMemorySessionService
from google.adk.types import Message, TextContent

agent = Agent(name="test_agent", model="gemini-3.5-flash", instruction="Say 'Hello world'.")
_session_service = InMemorySessionService()

async def main():
    try:
        runner = Runner(agent=agent, app_name="test_app", session_service=_session_service)
        print("Using run_async")
        async for event in runner.run_async(user_id="u1", session_id="s1", new_message="Hi"):
            print("Event type:", event.type)
            if event.type == "output":
                print("Data:", event.data)
                try:
                    print("Text:", event.data.text)
                except:
                    pass
    except Exception as e:
        import traceback
        traceback.print_exc()
asyncio.run(main())
