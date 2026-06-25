# 🤖 Jarvis Convention Assistant

An intelligent, proactive, truth-first anime and pop-culture convention companion built on the **Google Agent Development Kit (ADK)** and powered by **Gemini 2.0 Flash**. 

Designed to help attendees navigate crowded convention halls, plan itineraries, manage budgets, monitor real-time social media updates, and handle physical safety/emergencies deterministically.

---

## 🚀 Key Features & Guardrails

*   **Jarvis-Like Proactive Multi-Agent Core:** Coordinates a Master Planner and 12 dedicated specialist agents to handle complex requests.
*   **Deterministic Emergency Bypass (Safety First):** Fast-tracks physical safety and distress signals (e.g., panic, dehydration, feeling faint) directly to room/exit coordinates, bypassing LLM processing entirely.
*   **Robust Convention State:** Persistent, Pydantic-based state tracking (`ConventionState`) detailing budgets, user itineraries, cosplay logistics, energy levels, food preferences, and trusted source records.
*   **Source Verification & Provenance Layer:** Restricts hallucination by assigning trust scores and source metadata to every piece of information.
*   **Strict Data Hierarchy:** Enforces an override chain: `EventDataAPI` (Authoritative Ground Truth) > `Official Announcements` > `Official Social` > `Unofficial Social / Reddit`.
*   **Persistent SQLite Session Memory:** Retains budgets, preferences, and itineraries across multiple CLI or interactive sessions.
*   **Clean Repository Hygiene:** Dev scripts are cleanly isolated in a dedicated `dev/` directory to keep the root directory neat and production-ready.

---

## 📁 Project Structure Breakdown

The codebase is structured to enforce strong separation of concerns, deterministic guardrails, and persistent multi-agent orchestration.

```text
con-planner-adk/
├── agents/                       # Multi-Agent Coordination & Specialists
│   ├── __init__.py
│   ├── master_planner.py         # Top-level coordinator routing queries to 12 specialists
│   ├── emergency_agent.py        # Safety triage & physical exit/medical navigation (highest priority)
│   ├── schedule_agent.py         # Panel scheduling, timing, and conflict checks (EventDataAPI-only)
│   ├── budget_agent.py           # Spending tracking, purchase limits, and budget alerts
│   ├── maps_agent.py             # Booth/room coordinates and venue navigation
│   ├── merch_agent.py            # Vendor lists, merchandise details, and pricing
│   ├── social_agent.py           # Parsing of announcements, social media, and community reports
│   ├── food_agent.py             # Food vendors, hydration, and dietary restrictions
│   ├── weather_agent.py          # Outdoor forecast and recommendation stubs
│   ├── crowd_agent.py            # Queue/line estimates and capacity checks
│   ├── hotel_agent.py            # Hotel lodging, commute, and shuttle tracking
│   ├── memory_agent.py           # Energy level tracking and user profile personalization
│   └── verification_agent.py     # Source validation and explaining the trust-tier system
├── state/                        # State Serialization & Models
│   ├── __init__.py
│   └── convention_state.py       # Pydantic state model for session tracking & budget logs
├── verification/                 # Trust & Verification Engine
│   ├── __init__.py
│   └── source_verifier.py        # SourceTrust tier scoring, stale checking, and override precision logic
├── dev/                          # Developer Staging & Inspect Scripts
│   └── inspect_*.py              # Isolated scripts for inspecting ADK sessions, runners, and types
├── agent.py                      # Production entrypoint & deterministic ConventionPlannerAgent wrapper
├── event_data_api.py             # authoritative ground-truth data fetcher (OFFICIAL_API tier)
├── rag_retriever.py              # Semantic RAG retrieval cache & ingestion whitelisting filtering
├── runner.py                     # ADK Runner integration with async stream handling & auto-session creation
├── session_service.py            # SQLite database service for persisting session state
├── main.py                       # Unified command-line CLI interface
├── requirements.txt              # Project package dependencies
├── test_evals.py                 # Pytest suite with 13 comprehensive integration/unit tests
├── ax_data.json                  # Autoritative database file for AX (Anime Expo) 2026
├── .env.example                  # Environment variable configuration template
└── README.md                     # Project documentation (this file)
```

### File-by-File Details
*   [agents/master_planner.py](file:///C:/Users/Sanskar/con-planner-adk/agents/master_planner.py): Configures the main coordinate `Agent` utilizing `gemini-2.0-flash`. Instructs the model on the truth-first directives, multi-intent synthesis, and wires all 12 sub-agents.
*   [agents/emergency_agent.py](file:///C:/Users/Sanskar/con-planner-adk/agents/emergency_agent.py): Uses keyword-based triggers (`panic`, `help`, `hurt`, `faint`) to immediately return directions to first-aid stations or exits.
*   [state/convention_state.py](file:///C:/Users/Sanskar/con-planner-adk/state/convention_state.py): Implements the persistent `ConventionState` schema. Calculates remaining budgets, appends itinerary entries, and formats user preferences.
*   [verification/source_verifier.py](file:///C:/Users/Sanskar/con-planner-adk/verification/source_verifier.py): Computes confidence scores (ranging from 1.0 down to 0.0) based on source origin and staleness (stale data confidence is penalized by 30%).
*   [event_data_api.py](file:///C:/Users/Sanskar/con-planner-adk/event_data_api.py): Authorized wrapper for querying the `ax_data.json` database. Returns records with `SourceTier.OFFICIAL_API` stamps.
*   [rag_retriever.py](file:///C:/Users/Sanskar/con-planner-adk/rag_retriever.py): Semantic query engine for social feeds/rumors. Filters out social noise unless they contain structured logistical markers (e.g., "at", "pm", "stage", "booth").
*   [runner.py](file:///C:/Users/Sanskar/con-planner-adk/runner.py): Boots the Google ADK `Runner` with `auto_create_session=True` so that new user sessions do not fail with `SessionNotFoundError`. Extracts text streams using `event.is_final_response()`.
*   [session_service.py](file:///C:/Users/Sanskar/con-planner-adk/session_service.py): Integrates a SQLite database connection to serialize/deserialize the Pydantic `ConventionState` model, preventing state loss between CLI calls.

---

## 🏗️ Architecture FAQ

### 1. Why did you use `LlmAgent` vs. a simple function chain for routing?
Attendee queries are rarely neat, single-intent inputs. A query like: *"I have $100, where is the HoYoverse booth, and can I afford the $40 art book?"* spans three separate specialist domains (Memory/Budget, Maps, and Merchandise).
*   **Dynamic Intent Synthesis:** A simple function chain would require complex regexes or classifier pipelines to split the query, call the sub-systems in order, and merge their inputs. The `LlmAgent` (configured as Jarvis in [agents/master_planner.py](file:///C:/Users/Sanskar/con-planner-adk/agents/master_planner.py)) handles this natively. It uses the LLM to dynamically determine which tools or sub-agents to trigger, coordinates their responses, and synthesizes a singular natural language answer.
*   **Semantic Flexibility:** A function chain is brittle. If a user asks *"My wallet is empty, is it okay to grab a figure?"*, a keyword router might fail, whereas the LLM recognizes "wallet empty" as a budget query and "figure" as merchandise, routing to the appropriate specialists.
*   **Conversational Continuity & Proactivity:** The `LlmAgent` is instructed to check state variables (like fatigue or budget limits) and proactively recommend actions (e.g., suggesting a food break or warning about travel time between distant booths), which would be highly complex to orchestrate in a procedural code chain.

### 2. What does ADK's `Runner` actually do when you call `run_async`?
The `Runner` serves as the runtime environment that executes an ADK `Agent`. When you call `runner.run_async`:
1.  **Session & State Resolution:** It fetches or instantiates the conversation session using the provided `SessionService` (managing message history and execution variables).
2.  **Context Injection:** It loads the target agent's system instructions, tool definitions, and wraps them alongside current conversation history to build the LLM request.
3.  **Asynchronous Tool Loop:** It streams events from the model. If the model determines it needs to call a tool (e.g., `get_panel_info`), the runner intercepts the function call request, executes the corresponding python tool function locally, injects the function's result back into the message history, and re-invokes the model.
4.  **Event Output Generation:** It yields an asynchronous stream of execution events. These include intermediate steps, call traces, and final text chunks. In [runner.py](file:///C:/Users/Sanskar/con-planner-adk/runner.py), we iterate over this stream, detecting the final outputs using `event.is_final_response()` to compile the agent's finalized reply.

### 3. Why is the RAG retriever a separate layer from the `EventDataAPI`? What failure mode does that separation protect against?
The `EventDataAPI` handles authoritative data (schedules, room coordinates), while the `RAGRetriever` handles unstructured external feeds (social updates, Reddit hype, unofficial rumors).
*   **Isolating "Ground Truth" from "Speculation":** Merging them into a single data layer creates a high risk of **hallucinated updates**. If a social media scraping feed says *"Wuthering Waves showcase starting early at 1:30 PM!"*, storing it in the same database table as the official schedule could overwrite the verified time (2:00 PM). Separating the layers prevents RAG data from ever polluting the authoritative records.
*   **Ingestion Poisoning (Logistical Noise):** Unstructured data is full of spam and non-logistical commentary. By keeping RAG separate, we can apply an *Ingestion Filtering Guardrail* at the retrieval step: any social payload that does not contain structural logistical keywords (like "at", "pm", "stage", "booth") is silently dropped, protecting the model's context window from noise.
*   **Explicit Override Orchestration:** Because they are separate, the system can enforce a deterministic override check. Official API data always takes precedence. If both layers return a matching item, the system completely suppresses the RAG result or labels it explicitly as unverified.

### 4. What happens when `search_rag_information` returns a result that contradicts `get_schedule_info`? How does the agent decide?
The agent resolves this conflict using the **Source Verification & Provenance Hierarchy** defined in [verification/source_verifier.py](file:///C:/Users/Sanskar/con-planner-adk/verification/source_verifier.py):
1.  **Trust-Score Weights:** Each source is assigned a confidence score:
    *   `OFFICIAL_API` $\rightarrow$ 1.0 (Ground Truth)
    *   `OFFICIAL_ANNOUNCEMENT` $\rightarrow$ 0.95
    *   `OFFICIAL_SOCIAL` $\rightarrow$ 0.8
    *   `USER_PROVIDED` $\rightarrow$ 0.5
    *   `UNOFFICIAL_SOCIAL` (Reddit/Twitter rumor) $\rightarrow$ 0.3
2.  **Deterministic Hierarchy Overrides:** In [agent.py](file:///C:/Users/Sanskar/con-planner-adk/agent.py), the processor first pulls schedule data directly from `EventDataAPI.get_schedule()`. If a record matches, it returns it with the tag `(confirmed via official event data)`.
3.  **Suppression of Contradictory Rumors:** If a rumor exists in the RAG cache stating a different time or room (e.g., Genshin Impact panel at 12:00 PM Stage B) but the EventDataAPI confirms it is at 11:00 AM Main Stage, the RAG output is completely suppressed. This override logic is validated by integration tests `test_override_precision_genshin` and `test_override_precision_wuthering` in [test_evals.py](file:///C:/Users/Sanskar/con-planner-adk/test_evals.py).
4.  **Provenance Tagging:** If unverified social information must be presented (e.g. no official record exists yet), the agent is forced by its system instructions to append the exact trust label (e.g., `reported by unofficial source` or `not verified`) to ensure the user is fully aware of the risk.

### 5. Why are `sub_agents=[]` if the README talks about triage-nav and schedule sub-agents?
If you saw `sub_agents=[]` in any script, it was an artifact of an outdated draft or a test configuration file.
*   **The History:** The initial repository commit (`f83d6ce`) uploaded an early draft of the README that described a plan utilizing a `.agents/skills/` directory structure with `SKILL.md` files (like `triage-nav` and `schedule`).
*   **The Refactor:** In subsequent development (commit `966ed01`), this was replaced by a more robust, flat multi-agent topology. Rather than reading raw Markdown skill files, the architecture was fully refactored into **12 specialized programmatic agents** in the `agents/` package.
*   **Current Production Wiring:** In the active codebase inside [agents/master_planner.py](file:///C:/Users/Sanskar/con-planner-adk/agents/master_planner.py), the `sub_agents` parameter **is NOT empty**. It explicitly wires all 12 specialist agents:
    ```python
    master_planner = Agent(
        name="jarvis_convention_assistant",
        model="gemini-2.0-flash",
        instruction=MASTER_PLANNER_INSTRUCTION,
        sub_agents=[
            emergency_agent,
            schedule_agent,
            budget_agent,
            maps_agent,
            merch_agent,
            social_agent,
            food_agent,
            weather_agent,
            crowd_agent,
            hotel_agent,
            memory_agent,
            verification_agent,
        ],
    )
    ```
    This coordinates all specialist skills programmatically under a unified LLM router.

---

## 🛠️ Setup & Installation

Follow these steps to set up and run the Jarvis Convention Assistant locally.

### Prerequisites
*   **Python:** Version 3.10, 3.11, or 3.12 is recommended.
*   **Gemini API Key:** Required to run the LLM-powered multi-agent planner.

### Steps
1.  **Clone or Navigate to the Directory:**
    ```bash
    cd con-planner-adk
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the Virtual Environment:**
    *   **Windows (PowerShell):**
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    *   **macOS / Linux:**
        ```bash
        source .venv/bin/activate
        ```

4.  **Install All Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Your API Key:**
    Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
    Open `.env` in your text editor and enter your Gemini API key:
    ```env
    GEMINI_API_KEY=AIzaSy...
    ```
    > 🔑 Get your API key at [Google AI Studio](https://aistudio.google.com/apikey).

---

## 💻 Running the Assistant

The CLI tool supports multiple operational modes to test and interact with Jarvis.

### 1. Single Query Mode
Send a single query to Jarvis and receive a response:
```bash
python main.py query "Where is the HoYoverse booth and when is the Genshin Impact panel?"
```

### 2. Interactive Chat Mode
Start a conversational session that tracks your preferences, itinerary, and budget in real time:
```bash
python main.py interactive --session-id MyConTrip
```
*Type `exit` or `quit` to end the chat session.*

### 3. Retrieve Convention State
Inspect the current saved convention state (budget logs, saved booths, alerts) for a specific session ID:
```bash
python main.py status --session-id MyConTrip
```

### 4. Show Today's Plan
Print the full convention schedule loadout from the authoritative `EventDataAPI`:
```bash
python main.py plan
```

---

## 🧪 Verification & Evaluations

Run the comprehensive pytest suite to verify safety bypasses, source provenance, override checks, and cross-agent coordination:
```bash
python main.py test
```
*(Alternatively, run `pytest test_evals.py -v` directly inside your virtual environment).*

The suite includes **13 tests** checking key capabilities:
1.  **Synthesis check:** Merges panel schedules, budget, and location tracking in a single prompt.
2.  **Override precision (Genshin):** Confirms official API schedules take precedence over conflicting RAG cache rumors.
3.  **Override precision (Wuthering):** Assures official panel coordinates override unverified RAG inputs.
4.  **State continuity:** Verifies SQLite database saves preferences and budgets across interaction steps.
5.  **Emergency triage bypass:** Ensures distress inputs (e.g. panic/injury) bypass the LLM and return exit coordinates instantly.
6.  **Ingestion filtering:** Checks that social media items without logistical variables are discarded by the RAG retriever.
7.  **Source provenance:** Confirms all EventDataAPI operations return facts stamped with `OFFICIAL_API` tier.
8.  **Unverified label tagging:** Checks that unverified social items retrieve appropriate trust/confidence labels.
9.  **Master planner validation:** Ensures the coordination agent contains all 12 specialized sub-agents.
10. **Budget warning alerts:** Tests that overspending triggers warnings on remaining funds.
11. **Official-only mode:** Validates that enabling official-only mode suppresses unofficial social rumors entirely.
12. **Convention state model:** Exercises Pydantic serialization, alerts, itinerary items, and budgets.
13. **Verification tool rules:** Tests classification logic mapping text source names to SourceTiers.

---

## 🏷️ GitHub Repository Setup

To update the repository description and topics on GitHub, use the GitHub CLI:
```bash
gh repo edit --description "Jarvis Convention Assistant — An intelligent, proactive, truth-first anime convention companion built on Google ADK." --add-topic google-adk --add-topic gemini --add-topic multi-agent --add-topic anime --add-topic convention
```
