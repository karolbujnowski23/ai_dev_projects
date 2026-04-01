# Windpower Task: Multi-Agent Architecture Plan (As Built)

This document outlines the final, implemented Python-based asynchronous architecture used to solve the time-critical `windpower` task within the 40-second constraint. It reflects the discoveries and refinements made during development.

## 1. Problem Statement & Constraints
*   **Goal:** Configure a wind turbine schedule to produce necessary power for a power plant while protecting the turbine from extreme wind.
*   **Time Limit:** 40 seconds maximum execution time from the start of the service window. Linear execution will fail.
*   **API Endpoint:** `https://hub.ag3nts.org/verify`
*   **API Behavior:** Most functions are queued asynchronously. Requests are sent, and results must be polled via an `action: "getResult"` endpoint. Responses arrive in random order and can only be fetched once.
*   **Complex Rules (Refined):**
    *   **Storms:** Wind speeds >= 14 m/s. The turbine must be placed in a protective mode (`pitchAngle` = 90, `turbineMode` = "idle") exactly at the time of the storm.
    *   **Recovery:** The turbine returns to standard settings ~1 hour after a storm. *Discovery: The API only required a specific number of config points (in this case, 4: 3 storms + 1 production). The +1h reset configurations were explicitly rejected by the API as invalid.*
    *   **Production:** Find a weather window between 4 m/s and 14 m/s where the generated power (calculated via `14kW * YieldPercent * PitchEfficiency`) matches the `powerDeficitKw` required by the `powerplantcheck`.
    *   **Cryptography:** Configurations must be signed with an MD5-like unlock code obtained from `unlockCodeGenerator` using `startDate`, `startHour`, `windMs`, and `pitchAngle`.
    *   **Validation:** A test (`get` with `param: "turbinecheck"`) must be queued before the final `done` action.

## 2. Architectural Design: Asynchronous Multi-Agent (Blackboard Pattern)

To handle the 40-second constraint and random-order polling, the architecture relies on specialized, non-blocking Python `asyncio` tasks (Agents) communicating through a central shared state (Blackboard) within a single script (`main.py`).

### A. The Blackboard (Shared State)
*   **Role:** The central knowledge base and state holder.
*   **Mechanism:** Utilizes `asyncio.Event` (for triggering phases) and standard dictionaries/lists for routing data.
*   **Data Stored:** API Key (`APIKEY` from `.config`), API URL (`https://hub.ag3nts.org/verify`), Discovered Endpoints, Weather Data, Turbine Specs, Power Deficit, Unlock Codes, and the Final Draft Schedule.

### B. Orchestrator Agent (The Manager)
*   **Role:** Controls the workflow state machine and enforces the deadline.
*   **Workflow:**
    1.  Triggers `start`.
    2.  Commands `ActionAgent` to fire data requests (`weather`, `turbinecheck`, `powerplantcheck`) concurrently. *Discovery: Bypassed the `help` endpoint to save ~5 seconds, as the required endpoints were static and discovered during testing.*
    3.  Waits for data to be populated on the `Blackboard`.
    4.  Commands `IntelligenceAgent` to create the schedule.
    5.  Commands `CryptographyAgent` to sign the schedule.
    6.  Commands execution of `config`, `get` with `param: "turbinecheck"`, and `done` in sequence.

### C. Action Agent (The API Dispatcher)
*   **Role:** Exclusively responsible for sending outgoing API commands to Centrala.
*   **Behavior:** Fire-and-forget. It sends non-blocking HTTP POST requests (`aiohttp`) to the API. It logs synchronous responses (like the final `done` flag or queue confirmations) directly.
*   **Format:** Wraps all payloads in `{"apikey": "...", "task": "windpower", "answer": {"action": "..."}}`.

### D. Polling Agent (The Listener)
*   **Role:** Runs in a continuous, aggressive `asyncio` loop.
*   **Behavior:** Continuously sends `action: "getResult"`.
*   **Logic:** Parses incoming JSON, identifies the data type via the `sourceFunction` or specific keys (e.g., `unlockCodeGenerator`), and writes it to the `Blackboard`. Handles the rule that responses arrive randomly and can only be fetched once. Ignores "Queue empty" (Code 11) messages to prevent log spam.

### E. Intelligence Agent (The Analyst - Deterministic Python)
*   **Role:** Triggered by the Orchestrator when raw data is ready. Calculates the optimal wind turbine schedule.
*   **Refinement from Plan:** *Switched from an LLM (OpenRouter) to deterministic Python logic.* The LLM approach, while capable, added unpredictable latency (5-15 seconds) and ran the risk of formatting errors under the strict 40-second limit. Deterministic parsing executed in <10 milliseconds and proved more reliable.
*   **Logic:**
    1.  Parses the target `powerDeficitKw` (e.g., "3-4").
    2.  Iterates through the `weather` array.
    3.  Identifies "storms" (`windMs` >= 14) and schedules `pitchAngle`: 90, `turbineMode`: "idle".
    4.  Calculates yield for non-storm windows based on `windMs` (interpolated yield curve) and `pitchAngle` (0 = 100%, 45 = 65%).
    5.  Selects the first window where calculated power matches the deficit and schedules `turbineMode`: "production".

### F. Cryptography Agent (The Signer)
*   **Role:** Handles the generation of unlock codes for the schedule.
*   **Logic:** Once the Intelligence Agent drafts the schedule, this agent uses the Action Agent to request `unlockCodeGenerator` concurrently for every timestamp. It maps the asynchronous responses back to the correct schedule entry using the `startDate` and `startHour` returned in the `signedParams` of the response.

## 3. Technology Stack & Logging Strategy

*   **Core:** `asyncio` for the event loop, concurrency, and inter-agent communication.
*   **Networking (Centrala):** `aiohttp` for high-speed, non-blocking HTTP requests.
*   **Configuration:** `python-dotenv` for loading the `APIKEY` from the `../.config` file.
*   **Logging:** A robust logging setup using the standard `logging` module (`utils/logger.py`). Every raw JSON response received from the `PollingAgent` is immediately written to a timestamped file (`logs/api_responses_<timestamp>.log`) for debugging and audit.

## 4. Final Folder Structure

```
C:\\Users\\buyak\\Documents\\AI_devs\\zadania\\Z0402/
│
├── architecture_plan.md        # This file, documenting the final architecture.
├── main.py                     # The main entry point for the solution.
├── requirements.txt            # Python dependencies (aiohttp, python-dotenv).
├── logs/                       # Directory for storing runtime logs.
│   └── api_responses_...log    # Contains all raw JSON from the API for a given run.
│
└── windpower/                  # The main Python package for the solution.
    ├── __init__.py             # Makes 'windpower' a package.
    ├── blackboard.py           # Defines the Blackboard class for shared state.
    └── agents/                 # Contains all individual agent classes.
        ├── __init__.py
        ├── action.py           # ActionAgent: Sends commands to the API.
        ├── crypto.py           # CryptographyAgent: Handles unlock codes.
        ├── intelligence.py     # IntelligenceAgent: Calculates the schedule.
        ├── orchestrator.py     # OrchestratorAgent: Controls the main workflow.
        └── polling.py          # PollingAgent: Retrieves results from the API queue.
```

## 5. Execution Timeline (The Successful 33.79s Run)

*   **T = 0s:** Orchestrator triggers `start`; Polling Agent begins loop.
*   **T = ~0.5s:** Orchestrator fires concurrent requests for Weather, State, and Deficit.
*   **T = ~10s:** Polling Agent catches the Power Deficit Data.
*   **T = ~12s:** Polling Agent catches the Turbine State Data.
*   **T = ~24s:** Polling Agent catches the Weather Data (API heavily delays this).
*   **T = ~24.01s:** Intelligence Agent calculates the 4-point schedule in milliseconds.
*   **T = ~24.02s:** Cryptography Agent fires concurrent requests for all 4 unlock codes.
*   **T = ~26-28s:** Polling Agent catches all 4 unlock codes. Cryptography Agent signs the draft plan.
*   **T = ~28s:** Orchestrator fires `config` with the 4 signed configurations. API accepts them synchronously.
*   **T = ~29s:** Orchestrator fires `get` with `param: "turbinecheck"`.
*   **T = ~33s:** Orchestrator fires `done`.
*   **T = ~33.79s:** Action Agent catches the synchronous success response containing the FLAG. Task Complete.
