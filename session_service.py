import time
from typing import Dict, Any, List, Optional

class DiscordSessionService:
    def __init__(self):
        # Maps user_id or session_id to session data
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": time.time(),
                "last_active": time.time(),
                "history": [],
                "budget": None,
                "current_expenses": 0.0,
                "planned_purchases": [],
                "last_query": None,
                "domain_state": {}
            }
        else:
            self.sessions[session_id]["last_active"] = time.time()
        return self.sessions[session_id]

    def add_interaction(self, session_id: str, user_query: str, agent_response: str):
        session = self.get_or_create_session(session_id)
        session["history"].append({
            "timestamp": time.time(),
            "query": user_query,
            "response": agent_response
        })
        session["last_query"] = user_query

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        session = self.get_or_create_session(session_id)
        return session["history"]

    def set_budget(self, session_id: str, budget: float):
        session = self.get_or_create_session(session_id)
        session["budget"] = budget

    def get_budget(self, session_id: str) -> Optional[float]:
        session = self.get_or_create_session(session_id)
        return session["budget"]

    def add_purchase(self, session_id: str, item_name: str, cost: float):
        session = self.get_or_create_session(session_id)
        session["planned_purchases"].append({"item": item_name, "cost": cost})
        session["current_expenses"] += cost

    def get_expenses(self, session_id: str) -> float:
        session = self.get_or_create_session(session_id)
        return session["current_expenses"]

    def get_last_query(self, session_id: str) -> Optional[str]:
        session = self.get_or_create_session(session_id)
        return session["last_query"]

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
