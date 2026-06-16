import pytest
from agent import ConventionPlannerAgent
from event_data_api import EventDataAPI
from rag_retriever import RAGRetriever
from session_service import DiscordSessionService

@pytest.fixture
def agent():
    return ConventionPlannerAgent()

def test_synthesis_check(agent):
    """
    Synthesis Check: Must accurately merge variables across domains
    (finding a booth, checking the schedule, and verifying budget in a single query).
    """
    session_id = "user_synthesis_test"
    query = "Where is the HoYoverse booth, when is the Genshin Impact Panel, and my budget is $50."
    
    response = agent.process_message(session_id, query)
    
    # Check that location of booth 101 is included
    assert "Booth 101" in response
    assert "X=15" in response
    assert "Y=25" in response
    
    # Check that Genshin panel schedule is included
    assert "11:00 AM" in response
    assert "Main Stage" in response
    
    # Check that budget is processed
    assert "Budget" in response
    assert "$50.00" in response

def test_override_precision_genshin(agent):
    """
    Override Precision: API overrides must trigger successfully on 100% of
    conflicting data tests against the RAG staging cache.
    For Genshin Impact: RAG rumor says 12:00 PM Stage B, API says 11:00 AM Main Stage.
    """
    session_id = "user_override_test_1"
    query = "When and where is the Genshin Impact Panel?"
    
    response = agent.process_message(session_id, query)
    
    # Assert Event Data API values are returned
    assert "11:00 AM" in response
    assert "Main Stage" in response
    
    # Assert conflicting RAG rumor values are overridden and NOT in the response
    assert "12:00 PM" not in response
    assert "Stage B" not in response

def test_override_precision_wuthering(agent):
    """
    Override Precision for Wuthering Waves:
    RAG rumor says 01:30 PM Main Stage, API says 02:00 PM Stage B.
    """
    session_id = "user_override_test_2"
    query = "When is the Wuthering Waves Showcase?"
    
    response = agent.process_message(session_id, query)
    
    # Assert Event Data API values are returned
    assert "02:00 PM" in response
    assert "Stage B" in response
    
    # Assert conflicting RAG rumor values are overridden and NOT in the response
    assert "01:30 PM" not in response
    assert "Main Stage" not in response

def test_state_continuity(agent):
    """
    State Continuity: The ADK session service must accurately recall user queries
    from prior interaction windows.
    """
    session_id = "user_continuity_test"
    
    # First interaction: Set budget
    response1 = agent.process_message(session_id, "Set my budget to $100")
    assert "$100" in response1
    
    # Second interaction: Ask for booth info (should recall the budget)
    response2 = agent.process_message(session_id, "Where is the HoYoverse booth?")
    assert "Booth 101" in response2
    assert "Budget" in response2
    assert "$100.00" in response2

def test_emergency_triage_bypass(agent):
    """
    Bypass standard multi-intent routing and return shortest-path deterministic
    routing via Maps API immediately if input contains distress parameters (rulestriage.md).
    """
    session_id = "user_emergency_test"
    query = "Emergency! I am hurt and lost, where is the exit?"
    
    response = agent.process_message(session_id, query)
    
    # Should bypass normal routing and return exit route immediately
    assert "[EMERGENCY TRIAGE ROUTING]" in response
    assert "Main Entrance Gate A" in response
    assert "X=10" in response
    assert "Y=20" in response
    
    # Standard multi-intent info should not be triggered/present
    assert "HoYoverse" not in response
    assert "Genshin" not in response

def test_ingestion_filtering():
    """
    Ingestion Filtering: Apply deterministic source whitelisting. Isolate event operational variables
    from promotional or social commentary. If social media extraction yields no structural logistical data, drop the payload.
    """
    # Query for "HoYoverse" which has social hype comment in RAG with no logistical variables
    query_hype = "HoYoverse acrylic standees are limited edition, you should buy them fast!"
    results_hype = RAGRetriever.query(query_hype, apply_filtering=True)
    
    # The social media commentary containing no logistics ("HoYoverse acrylic standees...") should be filtered out
    assert len(results_hype) == 0
    
    # Query for "Genshin" which has social rumor containing logistics (time, stage)
    query_logistics = "Genshin Impact Panel is rescheduled"
    results_logistics = RAGRetriever.query(query_logistics, apply_filtering=True)
    
    # The social media payload containing logistical data is preserved for override checks
    assert len(results_logistics) > 0
