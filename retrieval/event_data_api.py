"""
Event Data API — the authoritative source for convention data.

All data returned from this module is tagged with SourceTier.OFFICIAL_API,
the highest trust level in the system. This data systematically overrides
any conflicting data from the RAG retriever or social media sources.

Backward compatible: preserves all original static method signatures.
"""

import json
import time as time_module
from typing import Dict, Any, List, Optional
import os

from verification.source_verifier import SourceTier, SourceRecord, verify_claim


# Mock database representing the deterministic Event Data
EVENT_DB = {
    "nav": {
        "exits": ["Main Entrance Gate A", "South Emergency Exit", "North Gate B"],
        "hydration_stations": ["Water Fountain Near Booth 101", "Hydration Tent Hall 2"],
        "first_aid": ["First Aid Booth next to Main Stage", "Medical Room 102"],
        "map_coordinates": {
            "Main Entrance Gate A": {"x": 10, "y": 20},
            "South Emergency Exit": {"x": 50, "y": 80},
            "North Gate B": {"x": 90, "y": 10},
            "Water Fountain Near Booth 101": {"x": 12, "y": 25},
            "Hydration Tent Hall 2": {"x": 45, "y": 60},
            "First Aid Booth next to Main Stage": {"x": 30, "y": 40},
            "Medical Room 102": {"x": 80, "y": 50},
            "Booth 101": {"x": 15, "y": 25},
            "Booth 202": {"x": 40, "y": 62},
            "Main Stage": {"x": 30, "y": 38}
        }
    }
}


def _data_dir() -> str:
    """Return directory containing ax_data.json (same dir as this file or project root)."""
    # Try project root first (backward compat), then this file's directory
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ax_data.json"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ax_data.json"),
        os.path.join(os.getcwd(), "ax_data.json"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return "ax_data.json"


def load_ax_data() -> Dict[str, Any]:
    """Load the authoritative convention data from ax_data.json."""
    try:
        with open(_data_dir(), "r") as f:
            return json.load(f)
    except Exception:
        return {"schedule": {}, "booths": {}, "metadata": {}}


class EventDataAPI:
    """
    Authoritative event data access layer.

    All methods preserve backward compatibility with the original API.
    New provenance-aware methods are added alongside the originals.
    """

    # ── Navigation (original API) ────────────────────────────────────────

    @staticmethod
    def get_exits() -> List[str]:
        return EVENT_DB["nav"]["exits"]

    @staticmethod
    def get_hydration_stations() -> List[str]:
        return EVENT_DB["nav"]["hydration_stations"]

    @staticmethod
    def get_first_aid() -> List[str]:
        return EVENT_DB["nav"]["first_aid"]

    @staticmethod
    def get_coordinates(location_name: str) -> Optional[Dict[str, float]]:
        return EVENT_DB["nav"]["map_coordinates"].get(location_name)

    # ── Schedule (original API) ──────────────────────────────────────────

    @staticmethod
    def get_schedule() -> Dict[str, Any]:
        return load_ax_data().get("schedule", {})

    @staticmethod
    def get_panel_info(panel_name: str) -> Optional[Dict[str, Any]]:
        """Match case-insensitively or via partial match."""
        schedule = EventDataAPI.get_schedule()
        for key, val in schedule.items():
            if panel_name.lower() in key.lower():
                return {"panel": key, **val}
        return None

    # ── Booths (original API) ────────────────────────────────────────────

    @staticmethod
    def get_booths() -> Dict[str, Any]:
        return load_ax_data().get("booths", {})

    @staticmethod
    def get_booth_by_name(booth_name: str) -> Optional[Dict[str, Any]]:
        booths = EventDataAPI.get_booths()
        for id, info in booths.items():
            if booth_name.lower() in info.get("name", "").lower() or booth_name.lower() in id.lower():
                return {"booth_id": id, **info}
        return None

    @staticmethod
    def get_booth_merchandise(booth_id: str) -> Dict[str, Any]:
        booth = EventDataAPI.get_booths().get(booth_id)
        if booth:
            return booth.get("merch", {})
        return {}

    # ── Metadata ─────────────────────────────────────────────────────────

    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        """Return convention metadata (name, dates, location, official sources)."""
        return load_ax_data().get("metadata", {})

    @staticmethod
    def get_official_sources() -> Dict[str, str]:
        """Return official source URLs for verification."""
        return load_ax_data().get("official_sources", {})

    # ── Provenance-tagged methods (new) ──────────────────────────────────

    @staticmethod
    def get_provenance(item_description: str) -> SourceRecord:
        """Create a SourceRecord for any item returned by this API."""
        return verify_claim(
            claim=item_description,
            source_name="EventDataAPI",
            tier=SourceTier.OFFICIAL_API,
        )

    @staticmethod
    def get_full_event_context() -> Dict[str, Any]:
        """Merge metadata + schedule + booths + navigation into one context payload."""
        data = load_ax_data()
        return {
            "metadata": data.get("metadata", {}),
            "schedule": data.get("schedule", {}),
            "booths": data.get("booths", {}),
            "official_sources": data.get("official_sources", {}),
            "navigation": EVENT_DB["nav"],
        }

    @staticmethod
    def get_schedule_with_provenance() -> List[Dict[str, Any]]:
        """Return schedule items each tagged with a SourceRecord."""
        schedule = EventDataAPI.get_schedule()
        results = []
        for name, details in schedule.items():
            record = EventDataAPI.get_provenance(
                f"{name}: {details.get('time', 'TBD')} at {details.get('location', 'TBD')}"
            )
            results.append({
                "event": name,
                "details": details,
                "source": record.model_dump(),
            })
        return results

    @staticmethod
    def get_booths_with_provenance() -> List[Dict[str, Any]]:
        """Return booth items each tagged with a SourceRecord."""
        booths = EventDataAPI.get_booths()
        results = []
        for booth_id, info in booths.items():
            record = EventDataAPI.get_provenance(
                f"Booth {booth_id}: {info.get('name', 'Unknown')}"
            )
            results.append({
                "booth_id": booth_id,
                "info": info,
                "source": record.model_dump(),
            })
        return results
