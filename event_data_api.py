import json
from typing import Dict, Any, List, Optional
import os

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

def load_ax_data():
    try:
        with open('ax_data.json', 'r') as f:
            return json.load(f)
    except Exception:
        return {"schedule": {}, "booths": {}}

class EventDataAPI:
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

    @staticmethod
    def get_schedule() -> Dict[str, Any]:
        return load_ax_data().get("schedule", {})

    @staticmethod
    def get_panel_info(panel_name: str) -> Optional[Dict[str, Any]]:
        # Match case-insensitively or via partial match
        schedule = EventDataAPI.get_schedule()
        for key, val in schedule.items():
            if panel_name.lower() in key.lower():
                return {"panel": key, **val}
        return None

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
