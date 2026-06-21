import asyncio
from google.adk import Runner
from google.genai import types
from google.adk.sessions import InMemorySessionService
from agent import root_agent

_session_service = InMemorySessionService()

EMERGENCY_KEYWORDS = ["emergency", "hurt", "exit", "water", "hydration", "panic", "first aid", "medical", "faint"]

def check_emergency(text: str):
    if not any(kw in text.lower() for kw in EMERGENCY_KEYWORDS):
        return None
    from event_data_api import EventDataAPI
    if "exit" in text.lower():
        loc = EventDataAPI.get_exits()[0]
    elif any(kw in text.lower() for kw in ["water", "hydration"]):
        loc = EventDataAPI.get_hydration_stations()[0]
    else:
        loc = EventDataAPI.get_first_aid()[0]
    coords = EventDataAPI.get_coordinates(loc)
    return f"[EMERGENCY TRIAGE ROUTING] Exit route requested. Nearest: {loc} (X={coords['x']}, Y={coords['y']}). Head there now."

async def send_to_agent(session_id: str, text: str):
    if (e := check_emergency(text)): return e
    
    new_message = types.UserContent(parts=[types.Part.from_text(text=text)])
    
    runner = Runner(agent=root_agent, session_service=_session_service, app_name="convention_planner")
    
    response_content = ""
    async for event in runner.run_async(user_id=session_id, session_id=session_id, new_message=new_message):
        if event.type == "output":
            response_content += event.data.text
    return response_content

def run(session_id: str, text: str):
    return asyncio.run(send_to_agent(session_id, text))
