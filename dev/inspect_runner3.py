import asyncio
from google.adk import Agent, Runner

agent = Agent(name="test_agent", model="gemini-3.5-flash")

async def main():
    try:
        runner = Runner(agent=agent, session_service=None)
        res = await runner.run_async("Hello")
        print(res.content)
    except Exception as e:
        print(e)
asyncio.run(main())
