"""
Convention Session Service.

Manages per-user session state using the ConventionState model.
Backward compatible: all original DiscordSessionService method signatures
are preserved (get_or_create_session, add_interaction, set_budget, etc.).
"""

import time
from typing import Dict, Any, List, Optional

from state.convention_state import ConventionState, ItineraryItem, HotelInfo


class ConventionSessionService:
    """Session service backed by ConventionState Pydantic models."""

    def __init__(self):
        self.sessions: Dict[str, ConventionState] = {}

    def get_or_create_session(self, session_id: str) -> ConventionState:
        if session_id not in self.sessions:
            self.sessions[session_id] = ConventionState(
                session_id=session_id,
                created_at=time.time(),
                last_active=time.time(),
            )
        else:
            self.sessions[session_id].touch()
        return self.sessions[session_id]

    def add_interaction(self, session_id: str, user_query: str, agent_response: str):
        session = self.get_or_create_session(session_id)
        session.interaction_history.append({
            "timestamp": time.time(),
            "query": user_query,
            "response": agent_response,
        })

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        session = self.get_or_create_session(session_id)
        return session.interaction_history

    def set_budget(self, session_id: str, budget: float):
        session = self.get_or_create_session(session_id)
        session.budget = budget

    def get_budget(self, session_id: str) -> Optional[float]:
        session = self.get_or_create_session(session_id)
        return session.budget

    def add_purchase(self, session_id: str, item_name: str, cost: float):
        session = self.get_or_create_session(session_id)
        session.log_expense(item_name, cost)

    def get_expenses(self, session_id: str) -> float:
        session = self.get_or_create_session(session_id)
        return session.current_expenses

    def get_last_query(self, session_id: str) -> Optional[str]:
        session = self.get_or_create_session(session_id)
        if session.interaction_history:
            return session.interaction_history[-1].get("query")
        return None

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    # ── New methods for the Jarvis architecture ──────────────────────────

    def add_alert(self, session_id: str, alert: str):
        session = self.get_or_create_session(session_id)
        session.add_alert(alert)

    def set_energy_level(self, session_id: str, level: int):
        session = self.get_or_create_session(session_id)
        session.energy_level = max(1, min(10, level))

    def add_itinerary_item(
        self,
        session_id: str,
        event_name: str,
        time: str = "TBD",
        location: str = "TBD",
        priority: int = 5,
    ):
        session = self.get_or_create_session(session_id)
        session.add_itinerary_item(ItineraryItem(
            event_name=event_name,
            time=time,
            location=location,
            priority=priority,
            source_tier="official_api",
        ))

    def set_hotel_info(
        self,
        session_id: str,
        name: str,
        address: str = "",
        checkin: str = "",
        checkout: str = "",
    ):
        session = self.get_or_create_session(session_id)
        session.hotel = HotelInfo(
            name=name,
            address=address,
            checkin=checkin,
            checkout=checkout,
        )

    def save_preference(self, session_id: str, key: str, value: Any):
        session = self.get_or_create_session(session_id)
        session.save_preference(key, value)

    def get_preference(self, session_id: str, key: str, default: Any = None) -> Any:
        session = self.get_or_create_session(session_id)
        return session.get_preference(key, default)

    def set_official_only_mode(self, session_id: str, enabled: bool):
        session = self.get_or_create_session(session_id)
        session.official_only_mode = enabled

    def get_state_summary(self, session_id: str) -> Dict[str, Any]:
        session = self.get_or_create_session(session_id)
        return session.get_state_summary()


# Backward compatibility alias
DiscordSessionService = ConventionSessionService
