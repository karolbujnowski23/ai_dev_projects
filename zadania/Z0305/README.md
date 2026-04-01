# Project Z0305 (savethem)

## Conception
This project is an automated agent designed to solve the **"savethem"** task. The objective is to calculate an optimal, shortest route for a messenger to reach the city of **Skolwin** to negotiate for wind turbine parts. 

The messenger starts with strict constraints: **10 units of food** and **10 units of fuel**. The agent must deduce the terrain layout, terrain traversal rules, and vehicle properties (fuel/food consumption rates) without having direct access to them initially. 

To achieve this, the agent interacts with a centralized `toolsearch` API to dynamically discover sub-tools, extracts the required intelligence (map, rules, vehicles), processes this data into a coherent rule set, and then employs an LLM to navigate the map, avoiding obstacles and resource exhaustion.

## Process Flow

The solution is driven by an Orchestrator pattern that breaks the task down into sequential phases, primarily handled in `app.py`:

1. **Phase 1: Discovery (`run_discovery`)**
   The system queries the `toolsearch` endpoint using various keywords (`map`, `terrain rules`, `vehicles`, `Skolwin`, etc.) to discover the hidden API endpoints that hold the necessary intelligence.

2. **Phase 1.5: Data Collection (`collect_data`)**
   Using the endpoints found in Phase 1, the agent intelligently queries these sub-tools (sometimes utilizing a reasoning LLM to craft the right query parameters) to extract the raw map grid, movement rules, and vehicle statistics.

3. **Phase 2: Prompt Creation (`generate_planner_prompt`)**
   The raw JSON data collected is passed to a prompt-engineering LLM (Gemini 2.5 Pro). The LLM processes this unstructured data and outputs a highly detailed, strict **System Prompt** (`planner_system_prompt.md`). This prompt serves as the "rulebook" for the pathfinding agent.

4. **Phase 3: Planner (`compute_path`)**
   A reasoning LLM (Gemini 3.1 Pro Preview) acts as the Planning Agent. It reads the rulebook and calculates the shortest valid sequence of moves (e.g., `["vehicle_name", "up", "right", ...]`), adhering to the strict 10 fuel / 10 food constraint.

5. **Phase 4: Submit & Feedback Loop (`verify_path`)**
   The generated path is submitted to the central `/verify` API. If the path is rejected (e.g., ran out of fuel, hit an obstacle), the orchestrator captures the failure reason and feeds it back to the Planning Agent. The Planner then retries the route calculation with the added context of its previous mistakes.

### Fast Iteration Loop (`app_loop.py`)
To prevent redundant API calls to the discovery and data collection endpoints during debugging, an alternative entry point `app_loop.py` was created. It skips Phases 1-2 and jumps directly to the Path Planning and Feedback Loop using the locally cached `planner_system_prompt.md`.

## File Structure

```text
Z0305/
├── README.md                   # This documentation file
├── Z0305text.md                # Original task narrative, constraints, and instructions
├── app.py                      # Main orchestrator running all phases from Discovery to Verification
├── app_loop.py                 # Fast-iteration orchestrator running only the path planning feedback loop
├── requirements.txt            # Python dependencies for the project
│
├── src/                        # Core source code modules
│   ├── api.py                  # Wrapper functions for LLM API interactions (Gemini/OpenRouter)
│   ├── config.py               # Environment configuration and API key loading
│   ├── logger.py               # Centralized logging configuration
│   ├── tools.py                # Core functions implementing Discovery, Data Collection, Pathfinding, etc.
│   └── query_reasoner.prompt.md# Prompt template used to dynamically craft API queries for discovered tools
│
├── output/                     # Cached artifacts generated during the pipeline
│   ├── discovered_tools.json   # Cached JSON of endpoints discovered via toolsearch
│   ├── raw_data.json           # Raw map, vehicle, and rules data collected from endpoints
│   └── planner_system_prompt.md# The synthesized rulebook generated for the Planning Agent
│
└── logs/                       # Application execution logs
    └── app.log                 # Main log file for the orchestrator processes
```
