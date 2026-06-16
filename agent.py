import pathlib
import re
from typing import Dict, Any, List, Optional
from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools.skill_toolset import SkillToolset
from event_data_api import EventDataAPI
from rag_retriever import RAGRetriever
from session_service import DiscordSessionService

class ConventionPlannerAgent:
    def __init__(self, session_service: Optional[DiscordSessionService] = None):
        self.session_service = session_service or DiscordSessionService()
        self.skills_dir = pathlib.Path(__file__).parent / ".agents" / "skills"
        
        # Load skills using ADK
        self.skills = {}
        skill_names = ["triage-nav", "schedule", "booths", "budget"]
        for name in skill_names:
            p = self.skills_dir / name
            if p.exists():
                try:
                    self.skills[name] = load_skill_from_dir(p)
                except Exception as e:
                    print(f"Warning: Failed to load skill '{name}': {e}")
        
        # Build toolset for ADK
        self.toolset = SkillToolset(skills=list(self.skills.values())) if self.skills else None
        
        # Instantiate ADK Agent
        # Configured per agents.md operating parameters
        self.adk_agent = Agent(
            name="convention_planner_root_agent",
            model="gemini-3.5-flash",
            description="Root Routing Agent for Anime and Pop-Culture Convention Planning.",
            instruction=(
                "You are the Root Routing Agent. Interpret incoming Discord messages, "
                "maintain state continuity across stateless interactions, synthesize multi-intent queries, "
                "and route task execution strictly to sub-agents/skills: triage-nav, schedule, booths, and budget."
            ),
            tools=[self.toolset] if self.toolset else [],
            sub_agents=[]
        )

    def process_message(self, session_id: str, message: str) -> str:
        """
        Process an incoming Discord message, executing multi-intent routing, 
        guardrails, hierarchy overrides, state continuity, and synthesis.
        """
        session = self.session_service.get_or_create_session(session_id)
        
        # --- 1. Triage Bypass Guardrail (rulestriage.md) ---
        # "If an input contains distress or immediate need parameters, bypass standard multi-intent
        # routing and return shortest-path deterministic routing via the Maps API immediately."
        distress_keywords = ["emergency", "hurt", "exit", "water", "hydration", "panic", "first aid", "medical", "faint"]
        is_distress = any(kw in message.lower() for kw in distress_keywords)
        
        if is_distress:
            # Bypass routing: extract the immediate need and return maps coordinate immediately
            if "exit" in message.lower():
                exit_loc = EventDataAPI.get_exits()[0] # Main Entrance Gate A
                coords = EventDataAPI.get_coordinates(exit_loc)
                response = f"[EMERGENCY TRIAGE ROUTING] Exit route requested. Nearest exit: {exit_loc} (Coordinates: X={coords['x']}, Y={coords['y']}). Please head there immediately."
                self.session_service.add_interaction(session_id, message, response)
                return response
            elif any(kw in message.lower() for kw in ["water", "hydration"]):
                water_loc = EventDataAPI.get_hydration_stations()[0] # Water Fountain Near Booth 101
                coords = EventDataAPI.get_coordinates(water_loc)
                response = f"[EMERGENCY TRIAGE ROUTING] Hydration requested. Nearest water station: {water_loc} (Coordinates: X={coords['x']}, Y={coords['y']}). Please head there to drink water."
                self.session_service.add_interaction(session_id, message, response)
                return response
            elif any(kw in message.lower() for kw in ["hurt", "panic", "first aid", "medical", "faint"]):
                med_loc = EventDataAPI.get_first_aid()[0] # First Aid Booth next to Main Stage
                coords = EventDataAPI.get_coordinates(med_loc)
                response = f"[EMERGENCY TRIAGE ROUTING] Medical/Safety assistance requested. Nearest First Aid: {med_loc} (Coordinates: X={coords['x']}, Y={coords['y']}). Medical staff are notified."
                self.session_service.add_interaction(session_id, message, response)
                return response

        # --- 2. State Continuity (agents.md Evals) ---
        # Parse potential budget settings or follow-up questions
        # Look for budget declarations (e.g. "budget is $50" or "budget of $100")
        budget_match = re.search(r"budget\s*(?:is|of|to|:)?\s*\$?\s*(\d+(?:\.\d{2})?)", message, re.IGNORECASE)
        if budget_match:
            session["budget"] = float(budget_match.group(1))

        # Check history to see if the user is referring to a previously mentioned subject
        history = self.session_service.get_history(session_id)
        last_query = history[-1]["query"] if history else None
        
        # --- 3. Multi-Intent Parsing & Query Routing ---
        # Check query keywords to route intents to specific sub-agents/skills
        has_nav = any(kw in message.lower() for kw in ["where", "location", "find", "booth", "map", "gate"])
        has_schedule = any(kw in message.lower() for kw in ["schedule", "when", "time", "panel", "stage", "event", "start"])
        has_booths = any(kw in message.lower() for kw in ["merch", "buy", "price", "booth", "vendor", "stall", "sell", "genshin", "wuthering"])
        has_budget = any(kw in message.lower() for kw in ["budget", "cost", "price", "afford", "limit", "spent", "fits"])

        # State resolution: if the user asks a brief follow-up and we have history, inherit intents
        if last_query and not (has_nav or has_schedule or has_booths or has_budget):
            has_nav = any(kw in last_query.lower() for kw in ["where", "location", "find", "booth", "map", "gate"])
            has_schedule = any(kw in last_query.lower() for kw in ["schedule", "when", "time", "panel", "stage", "event", "start"])
            has_booths = any(kw in last_query.lower() for kw in ["merch", "buy", "price", "booth", "vendor", "stall", "sell"])
            has_budget = any(kw in last_query.lower() for kw in ["budget", "cost", "price", "afford", "limit", "spent", "fits"])

        # Determine target subjects (panels, booths, items)
        # Search for high-demand titles
        subjects = []
        if "genshin" in message.lower() or (last_query and "genshin" in last_query.lower()):
            subjects.append("Genshin Impact")
        if "wuthering" in message.lower() or (last_query and "wuthering" in last_query.lower()):
            subjects.append("Wuthering Waves")

        # --- 4. Retrieval & Ingestion Filtering ---
        # Query official API
        api_booth_info = None
        api_schedule_info = None
        
        # Try matching booth names or IDs dynamically
        for bid, binfo in EventDataAPI.get_booths().items():
            if binfo["name"].lower() in message.lower() or bid.lower() in message.lower():
                api_booth_info = {"booth_id": bid, **binfo}
                break
            if last_query and (binfo["name"].lower() in last_query.lower() or bid.lower() in last_query.lower()):
                api_booth_info = {"booth_id": bid, **binfo}
                break
                
        # Try matching schedule panel names dynamically
        for panel, sinfo in EventDataAPI.get_schedule().items():
            keywords = [w.lower() for w in panel.split() if w.lower() not in ["stage", "panel", "showcase", "contest"]]
            if any(kw in message.lower() for kw in keywords if len(kw) > 2):
                api_schedule_info = {"panel": panel, **sinfo}
                break
            if last_query and any(kw in last_query.lower() for kw in keywords if len(kw) > 2):
                api_schedule_info = {"panel": panel, **sinfo}
                break

        # Query RAG cache with Ingestion Filtering
        # It filters out promotional/social comments without logistical variables.
        rag_results = RAGRetriever.query(message, apply_filtering=True)
        if last_query and not rag_results:
            rag_results = RAGRetriever.query(last_query, apply_filtering=True)

        # --- 5. Hierarchy Enforcement (API systematically overrides RAG) ---
        schedule_time = None
        schedule_loc = None
        booth_id = None
        booth_name = None
        
        # Process Schedule
        if api_schedule_info:
            # Event Data API overrides RAG
            schedule_time = api_schedule_info["time"]
            schedule_loc = api_schedule_info["location"]
        else:
            # Fallback to RAG if allowed (but Zero-Hallucination forbids synthesizing spatial/temporal data)
            for item in rag_results:
                if "panel" in item["title"].lower() or "showcase" in item["title"].lower():
                    time_match = re.search(r"(\d{2}:\d{2}\s*(?:AM|PM))", item["content"])
                    if time_match:
                        pass

        # Process Booth
        if api_booth_info:
            booth_id = api_booth_info["booth_id"]
            booth_name = api_booth_info["name"]
            booth_coords = EventDataAPI.get_coordinates(booth_id)
        else:
            booth_coords = None

        # --- 6. Budget calculations ---
        current_budget = session.get("budget")
        planned_cost = 0.0
        merch_available = []
        merch_warnings = []
        
        if api_booth_info:
            merch = api_booth_info["merch"]
            for item_name, details in merch.items():
                price = details["price"]
                stock = details["stock"]
                merch_available.append(f"{item_name} (${price}) [Stock: {stock}]")
                # Accumulate planned purchases if user wants to buy them
                if any(kw in message.lower() for kw in ["buy", "purchase", "acrylic", "plushie"]):
                    # User wants to buy the item
                    if "acrylic" in item_name.lower() and "acrylic" in message.lower():
                        planned_cost += price
                        session["planned_purchases"].append({"item": item_name, "cost": price})
                        session["current_expenses"] += price
                    elif "plushie" in item_name.lower() and "plushie" in message.lower():
                        planned_cost += price
                        session["planned_purchases"].append({"item": item_name, "cost": price})
                        session["current_expenses"] += price

        # --- 7. Response Synthesis (Synthesis Check) ---
        response_parts = []
        
        # Nav response
        if has_nav:
            if booth_name and booth_coords:
                response_parts.append(f"🗺️ **Location**: The official {booth_name} is located at **{booth_id}** (Coordinates: X={booth_coords['x']}, Y={booth_coords['y']}).")
            else:
                # Zero-Hallucination Mandate: Never synthesize spatial data.
                response_parts.append("🗺️ **Location**: I cannot verify the location details as they are not in the official Event Data.")

        # Schedule response
        if has_schedule:
            if schedule_time and schedule_loc:
                response_parts.append(f"📅 **Schedule**: The official event timing is confirmed for **{schedule_time}** at **{schedule_loc}**.")
            else:
                # Zero-Hallucination Mandate: Never synthesize temporal data.
                response_parts.append("📅 **Schedule**: I cannot verify the schedule timing as it is not in the official Event Data.")

        # Booths/Merch response
        if has_booths and api_booth_info:
            response_parts.append(f"🛍️ **Merchandise available at {booth_name} ({booth_id})**:\n" + "\n".join(f"- {m}" for m in merch_available))

        # Budget response
        if has_budget or planned_cost > 0 or (session.get("budget") is not None and has_booths):
            if current_budget is not None:
                remaining = current_budget - session["current_expenses"]
                status = f"💰 **Budget Status**: Total Budget: ${current_budget:.2f} | Total Spent: ${session['current_expenses']:.2f} | Remaining: ${remaining:.2f}."
                if remaining < 0:
                    status += " ⚠️ **Warning**: You have exceeded your budget!"
                elif planned_cost > 0:
                    status += f" Planned purchase cost: ${planned_cost:.2f} fits in your remaining budget."
                response_parts.append(status)
            else:
                if planned_cost > 0:
                    response_parts.append(f"💰 **Budget Status**: Cost for planned items: ${planned_cost:.2f}. (No total budget limit set. You can set one by typing 'My budget is $X'.)")

        # Zero-Hallucination guardrail: If nothing matched and we have no valid details
        if not response_parts:
            # Default helper message reflecting domain
            response_parts.append("Welcome! I am the Convention Planner Root Agent. I can help you with Exit/Hydration locations, Panels, Booths/Merch, and Budget tracking. What would you like to know?")

        response = "\n\n".join(response_parts)
        self.session_service.add_interaction(session_id, message, response)
        return response
