"""
Typed state model for the Jarvis convention assistant.

ConventionState is the single shared state object representing
the user's full convention context — budget, itinerary, preferences,
alerts, and provenance-tagged data.
"""

import time as time_module
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ItineraryItem(BaseModel):
    """A single event or activity in the user's convention plan."""
    event_name: str
    time: str = "TBD"
    location: str = "TBD"
    priority: int = 5  # 1 (highest) to 10 (lowest)
    notes: str = ""
    source_tier: str = "unknown"


class HotelInfo(BaseModel):
    """Lodging details for the convention trip."""
    name: str
    address: str = ""
    checkin: str = ""
    checkout: str = ""
    commute_notes: str = ""


class ConventionState(BaseModel):
    """
    The complete convention context for a single user session.

    Every specialist agent reads from and writes to this state.
    The Master Planner uses it to produce the final action plan.
    """
    session_id: str
    convention_name: str = "Unknown"

    # Budget & spending
    budget: Optional[float] = None
    current_expenses: float = 0.0
    planned_purchases: List[Dict[str, Any]] = Field(default_factory=list)

    # Itinerary
    itinerary: List[ItineraryItem] = Field(default_factory=list)

    # User preferences & personalization
    preferences: Dict[str, Any] = Field(default_factory=dict)
    dietary_preferences: List[str] = Field(default_factory=list)

    # Lodging & travel
    hotel: Optional[HotelInfo] = None
    travel_status: Optional[str] = None

    # Social
    friends: List[str] = Field(default_factory=list)

    # Physical state
    energy_level: int = 10  # 1–10 scale
    current_location: Optional[str] = None

    # Cosplay
    cosplay_schedule: List[str] = Field(default_factory=list)

    # Planning
    priorities: List[str] = Field(default_factory=list)
    time_remaining_hours: Optional[float] = None
    open_tasks: List[str] = Field(default_factory=list)
    alerts: List[str] = Field(default_factory=list)

    # History
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Timestamps
    created_at: float = Field(default_factory=time_module.time)
    last_active: float = Field(default_factory=time_module.time)

    # Mode flags
    official_only_mode: bool = False

    def add_alert(self, alert: str) -> None:
        """Add an alert if not already present."""
        if alert not in self.alerts:
            self.alerts.append(alert)

    def add_itinerary_item(self, item: ItineraryItem) -> None:
        """Add an event to the itinerary."""
        self.itinerary.append(item)

    def log_expense(self, item_name: str, cost: float) -> None:
        """Record a purchase and update running total."""
        self.planned_purchases.append({"item": item_name, "cost": cost})
        self.current_expenses += cost

    def get_budget_remaining(self) -> Optional[float]:
        """Return remaining budget, or None if no budget set."""
        if self.budget is not None:
            return self.budget - self.current_expenses
        return None

    def save_preference(self, key: str, value: Any) -> None:
        """Store a user preference."""
        self.preferences[key] = value

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Retrieve a user preference."""
        return self.preferences.get(key, default)

    def touch(self) -> None:
        """Update last_active timestamp."""
        self.last_active = time_module.time()

    def get_state_summary(self) -> Dict[str, Any]:
        """Return a compact summary for display or agent context."""
        return {
            "session_id": self.session_id,
            "convention": self.convention_name,
            "budget": self.budget,
            "spent": self.current_expenses,
            "remaining": self.get_budget_remaining(),
            "itinerary_count": len(self.itinerary),
            "alerts": self.alerts,
            "energy_level": self.energy_level,
            "priorities": self.priorities,
            "open_tasks": self.open_tasks,
            "official_only_mode": self.official_only_mode,
        }
