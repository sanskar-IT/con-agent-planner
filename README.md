# Jarvis Convention Assistant

An intelligent, proactive, truth-first convention companion built on the **Google Agent Development Kit (ADK)**. Designed to plan convention days end-to-end, monitor real-time changes (schedule, weather, crowd, merch, etc.), and provide verified guidance to pop-culture and anime convention attendees.

---

## 🚀 Key Features & Guardrails

- **Jarvis-Like Proactive Multi-Agent Core**: Coordinates a Master Planner and 12 dedicated specialist agents (Emergency, Schedule, Budget, Maps, Merch, Social, Food, Weather, Crowd, Hotel, Memory, and Verification) to handle complex requests.
- **Robust Convention State**: Tracks a rich state structure using `Pydantic` (`ConventionState`) detailing budgets, user itineraries, cosplay logistics, energy levels, food preferences, and trusted source records.
- **Source Verification & Provenance Layer**: Restricts hallucination by assigning trust scores and source metadata to every piece of information.
- **Strict Data Hierarchy**: Enforces a strict override chain (`EventDataAPI` > `Official Announcements` > `Official Social` > `Unofficial/Reddit`).
- **Emergency Pre-flight Bypass**: Instantly diverts distress signals (e.g. panic, emergency, feeling faint) to the Emergency Agent, bypassing the Master Planner and LLM routing entirely for safety.
- **Persistent Memory & State Continuity**: Preserves budgets, preferences, and itineraries across user sessions using a SQLite database backend.

---

## 📁 Project Structure

```text
con-planner-adk/
├── agents/                       # Specialist Agents
│   ├── __init__.py
│   ├── master_planner.py         # Main coordination and itinerary engine
│   ├── emergency_agent.py        # Triage and high-stress response (highest priority)
│   ├── schedule_agent.py         # Panel scheduling, timing, and conflicts
│   ├── budget_agent.py           # Purchase limits, alerts, and spending checks
│   ├── maps_agent.py             # Booth & room coordinates, venue navigation
│   ├── merch_agent.py            # Vendor lists, wishlist tracking, booth details
│   ├── social_agent.py           # Labeled announcements and social media streams
│   ├── food_agent.py             # Dietary limits, food/beverage recommendations
│   ├── weather_agent.py          # Real-time and forecasted outdoor condition check
│   ├── crowd_agent.py            # Line and room capacity/queue status
│   ├── hotel_agent.py            # Lodging info, check-in logistics, and shuttle times
│   ├── memory_agent.py           # User energy level tracker & custom preferences
│   └── verification_agent.py     # Source validation and provenance tagging
├── retrieval/                    # Data Ingestion and Mock APIs
│   ├── __init__.py
│   ├── event_data_api.py         # Official deterministic mock database API
│   └── rag_retriever.py          # Semantic staging cache and ingestion whitelist filter
├── state/                        # Application State Models
│   ├── __init__.py
│   └── convention_state.py       # Pydantic ConventionState & sub-models
├── verification/                 # Verification Engine
│   ├── __init__.py
│   └── source_verifier.py        # Implements SourceTrust tiers, override validation, and tagging
├── agent.py                      # Main entrypoint exposing ConventionPlannerAgent
├── runner.py                     # Execution wrapper with pre-flight bypass logic
├── session_service.py            # SQLite session memory manager
├── main.py                       # Command line interface
├── requirements.txt              # Dependencies
├── test_evals.py                 # Comprehensive pytest verification suite
├── ax_data.json                  # Local mock database for AX 2026
└── README.md                     # This file
```

---

## 🛠️ Setup & Installation

1. **Navigate to Project Directory**:
   ```bash
   cd con-planner-adk
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the Environment**:
   * **Windows (PowerShell)**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   * **macOS / Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Running the Assistant

The CLI supports interactive querying, single prompts, planning, status tracking, and running tests.

### 1. Single Query Mode
Send a single query to Jarvis:
```bash
python main.py query "I have $200. Is the Cyberpunk panel at 3pm, and can I afford the $150 jacket?"
```

### 2. Interactive Mode
Start a continuous session tracking your preferences and choices in real-time:
```bash
python main.py interactive --session-id MyConTrip
```

### 3. Retrieve Current State
View the convention state saved for a specific session ID:
```bash
python main.py status --session-id MyConTrip
```

### 4. Show Today's Plan
Print the official event schedule and metadata:
```bash
python main.py plan
```

---

## 🧪 Verification & Evaluations

Run the comprehensive pytest suite verifying safety bypasses, source provenance, override checks, and cross-agent coordination:
```bash
python main.py test
```
*(Alternatively, run `pytest test_evals.py -v` directly).*

The suite includes 13 test scenarios validating:
- **Synthesis check**: Merging panel schedules, budgets, and location tracking.
- **Override precision**: Ensuring API truths correctly override semantic RAG cache rumors.
- **Emergency bypass**: Fast-tracking distress alerts directly to coordinates without LLM latency.
- **State continuity**: Validating budget, energy levels, and preference persistence.
- **Advanced domains**: Verifying food requirements, merch updates, queue status, and weather alerts.
