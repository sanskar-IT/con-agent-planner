from typing import Dict, Any, List
from google.adk import Agent
from event_data_api import EventDataAPI
from rag_retriever import RAGRetriever

def get_schedule_info() -> Dict[str, Any]:
    """Get the official schedule of events."""
    return EventDataAPI.get_schedule()

def get_booth_info() -> Dict[str, Any]:
    """Get the official booth locations and merchandise."""
    return EventDataAPI.get_booths()

def search_rag_information(query: str) -> List[Dict[str, str]]:
    """Search for general convention information, rumors, and social commentary."""
    return RAGRetriever.query(query, apply_filtering=True)

# Build the Agent
root_agent = Agent(
    name="convention_planner_root_agent",
    model="gemini-3.5-flash",
    description="Root Routing Agent for Anime and Pop-Culture Convention Planning.",
    instruction=(
        "You are the Root Routing Agent. Interpret incoming Discord messages, "
        "synthesize multi-intent queries, and answer using the provided tools. "
        "Always use `get_schedule_info` for schedule queries, `get_booth_info` for booths/merch, "
        "and `search_rag_information` for general information. "
        "If something is not in the official data (tools), say 'not in official data yet'. "
        "Do not confabulate times or locations."
    ),
    tools=[get_schedule_info, get_booth_info, search_rag_information],
    sub_agents=[]
)
