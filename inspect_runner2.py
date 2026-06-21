import asyncio
from google.adk import Agent, Runner

def my_tool(x: int) -> str:
    """A tool."""
    return str(x * 2)

agent = Agent(name="test_agent", model="gemini-3.5-flash", tools=[my_tool])

async def main():
    runner = Runner(agent=agent)
    res = await runner.run_async("What is 5 times 2?")
    print("Result:", res)
    print("Content:", res.content)

asyncio.run(main())
