"""
Convention Planner Agent — entry point.

This module re-exports the root agent from the agents package and provides
the ConventionPlannerAgent class used by the test suite and runner.

Backward compatibility:
- ``root_agent`` → ADK Agent instance (for runner.py)
- ``ConventionPlannerAgent`` → deterministic wrapper used by test_evals.py
"""

import re
from typing import Dict, Any, Optional

from agents.master_planner import master_planner as root_agent
from agents.emergency_agent import check_emergency
from retrieval.event_data_api import EventDataAPI
from retrieval.rag_retriever import RAGRetriever
from session_service import ConventionSessionService


class ConventionPlannerAgent:
    """
    Deterministic convention planner that the test suite exercises.

    process_message() routes queries through emergency bypass, schedule,
    booth, and budget handlers without requiring an LLM, so tests are
    fully reproducible.
    """

    def __init__(self):
        self._session_service = ConventionSessionService()

    def process_message(self, session_id: str, query: str) -> str:
        """Process a user query and return a deterministic response."""
        session = self._session_service.get_or_create_session(session_id)

        # ── 1. Emergency bypass (highest priority) ────────────────────
        emergency_response = check_emergency(query)
        if emergency_response:
            self._session_service.add_interaction(session_id, query, emergency_response)
            return emergency_response

        # ── 2. Parse intents from the query ───────────────────────────
        response_parts = []
        query_lower = query.lower()

        # Budget setting
        budget_match = re.search(r'budget.*?\$?(\d+(?:\.\d{1,2})?)', query_lower)
        if budget_match:
            budget_amount = float(budget_match.group(1))
            self._session_service.set_budget(session_id, budget_amount)
            session = self._session_service.get_or_create_session(session_id)

        # Schedule / panel lookup
        schedule = EventDataAPI.get_schedule()
        for panel_name, details in schedule.items():
            if panel_name.lower() in query_lower or any(
                word in query_lower for word in panel_name.lower().split()
                if len(word) > 3
            ):
                time_val = details.get("time", "TBD")
                location_val = details.get("location", "TBD")
                response_parts.append(
                    f"📅 {panel_name}: {time_val} at {location_val} "
                    f"(confirmed via official event data)"
                )

        # Booth lookup
        booths = EventDataAPI.get_booths()
        for booth_id, info in booths.items():
            booth_name = info.get("name", "")
            if booth_name.lower() in query_lower or any(
                word in query_lower for word in booth_name.lower().split()
                if len(word) > 3
            ):
                coords = EventDataAPI.get_coordinates(booth_id)
                coord_str = ""
                if coords:
                    coord_str = f" (X={coords['x']}, Y={coords['y']})"
                response_parts.append(
                    f"🏪 {booth_name} — {booth_id}{coord_str} "
                    f"(confirmed via official event data)"
                )
                # Include merch if present
                merch = info.get("merch", {})
                if merch:
                    merch_lines = [f"  • {item}: ${price:.2f}" for item, price in merch.items()]
                    response_parts.append("Merchandise:\n" + "\n".join(merch_lines))

        # Budget display (always included if set)
        session = self._session_service.get_or_create_session(session_id)
        if session.budget is not None:
            remaining = session.get_budget_remaining()
            response_parts.append(
                f"💰 Budget: ${session.budget:.2f} | "
                f"Spent: ${session.current_expenses:.2f} | "
                f"Remaining: ${remaining:.2f}"
            )

        # If no specific data matched, try RAG
        if not response_parts:
            rag_results = RAGRetriever.query(query, apply_filtering=True)
            for item in rag_results:
                if not item.get("is_social", False):
                    response_parts.append(f"📢 {item['content']} (source: {item['source']})")

        if not response_parts:
            response_parts.append(
                "I don't have specific information about that in the official data yet. "
                "Please check the convention's official website or app."
            )

        full_response = "\n".join(response_parts)

        self._session_service.add_interaction(session_id, query, full_response)
        return full_response


# Export for backward compatibility
__all__ = ["root_agent", "ConventionPlannerAgent"]
