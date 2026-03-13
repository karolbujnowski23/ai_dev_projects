# Zadanie 2 — findhim

## File structure

```
zadanie2/
├── agent.py          # Main entry point — runs the agentic loop
├── tools.py          # Pure Python tool implementations (geo math + hub API calls)
├── tool_schemas.py   # JSON Schema definitions for LLM function-calling
└── README.md         # This file
```

The `.config` file lives at `./zadania/Z0102/.config` and must contain:
```
APIKEY=<your hub key>
LLM_APIKEY=<your OpenRouter key>
```

## How it works

```
agent.py
  │
  ├─ loads config (.config)
  ├─ defines SUSPECTS list (from S01E01 output)
  ├─ builds SYSTEM_PROMPT with suspect list
  │
  └─ run_agent()
       │
       ├─ sends messages + TOOL_SCHEMAS to OpenRouter (gpt-5-mini)
       │
       └─ agentic loop (max MAX_ITERATIONS):
            │
            ├─ LLM responds with tool_calls?
            │    └─ dispatch to TOOL_MAP  ──► tools.py functions
            │         └─ append tool result to messages
            │
            └─ LLM responds with text?
                 └─ print final answer & exit
```

## Agent tool sequence (expected)

1. `get_power_plant_locations()` → plant list
2. `get_person_locations(name, surname)` × 4 suspects
3. `find_closest_plant(person_locations, plants)` × 4 suspects
4. Identify suspect with minimum distance
5. `get_access_level(name, surname, birth_year)` for that suspect
6. `submit_answer(name, surname, access_level, power_plant_code)`

## Running

```bash
cd zadania/Z0102   # so .config is found by dotenv
python zadanie2/agent.py
```
