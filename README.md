# Convention Planner ADK Root Agent

A Python-based AI agent system built on the **Google Agent Development Kit (ADK)**. It serves as the Root Routing Agent for anime and pop-culture conventions (e.g., Comic Con), handling attendee queries, managing budgets, and directing navigation.

---

## 🚀 Key Features & Guardrails

- **Multi-Intent Routing**: Analyzes user queries and delegates tasks to specialized sub-agent skills (`triage-nav`, `schedule`, `booths`, `budget`).
- **Emergency Triage Bypass**: Instantly overrides standard routing to output map coordinates for exits, hydration, or medical aid when distress is detected (per `rulestriage.md`).
- **Hierarchy Enforcement**: Ensures that official deterministic data from the `Event Data API` systematically overrides semantic staging cache data from the `RAG Retriever` in all scenarios.
- **Ingestion Filtering**: Whitelists structural event logistics while filtering out social media chatter that contains no operational variables.
- **Zero-Hallucination Mandate**: Refuses to synthesize or approximate spatial coordinates or temporal events if they are missing from official sources.
- **State Continuity**: Utilizes a memory-backed Discord session service to maintain budgets and interaction history across stateless requests.

---

## 📁 Project Structure

```text
con-planner-adk/
├── .agents/
│   └── skills/
│       ├── triage-nav/
│       │   └── SKILL.md       # Safety, emergency routing, and hydration instructions
│       ├── schedule/
│       │   └── SKILL.md       # Panel timing and stage assignment instructions
│       ├── booths/
│       │   └── SKILL.md       # Vendor merchandise and availability instructions
│       └── budget/
│           └── SKILL.md       # Budget tracking and constraint instructions
├── event_data_api.py          # Official deterministic database mock
├── rag_retriever.py           # Unstructured staging cache and ingestion whitelister
├── session_service.py         # Discord-session memory manager
├── agent.py                   # Main routing agent utilizing google-adk
├── main.py                    # Typer command-line interface
├── test_evals.py              # Pytest verification suite
├── requirements.txt           # Python package requirements
└── README.md                  # Project documentation (this file)
```

---

## 🛠️ Setup & Installation

1. **Clone the Repository** (or navigate to the project directory):
   ```bash
   cd con-planner-adk
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the Environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Running the Agent

The CLI is powered by Typer and automatically configures standard output encoding for emoji rendering.

### 1. Run a Single Query
Send a single message to the agent using the default session:
```bash
python main.py query "Where is the HoYoverse booth and when is the Genshin Impact panel?"
```

### 2. Run Interactive Discord Chat Simulation
Simulate a stateless Discord channel. The session service will track your context:
```bash
python main.py interactive
```

### 3. Run Verification Tests
Verify all evaluation criteria (Synthesis, Override Precision, Triage Bypass, State Continuity) pass:
```bash
python main.py test
```

---

## 🧪 Evaluation Test Suite

Run unit tests directly with Pytest to verify the system guardrails:
```bash
pytest test_evals.py
```

It validates:
- **Synthesis Check**: Verifies that queries seeking location, schedules, and budgets are correctly answered.
- **Override Precision**: Confirms Event Data overrides outdated RAG rumors (100% precision).
- **State Continuity**: Checks if the agent recalls budget bounds from prior interaction cycles.
- **Emergency Bypass**: Tests if distress signals instantly return map coordinates.
