import requests
import json
import os
import math
from dotenv import load_dotenv
from typing import Any
import tools
import tool_schemas
from tool_schemas import TOOL_SCHEMAS
from tools import (
    get_power_plant_locations as _get_plants,
    get_person_locations as _get_locs,
    get_access_level as _get_access,
    find_closest_plant,
    submit_answer as _submit,
    geocode_city,
)

# 2. wrappers (defined first)
def get_power_plant_locations():
    return _get_plants(HUB_BASE, HUB_APIKEY)

def get_person_locations(name: str, surname: str):
    return _get_locs(HUB_BASE, HUB_APIKEY, name, surname)

def get_access_level(name: str, surname: str, birth_year: int):
    return _get_access(HUB_BASE, HUB_APIKEY, name, surname, birth_year)

def submit_answer(name: str, surname: str, access_level: int, power_plant_code: str):
    return _submit(HUB_BASE, HUB_APIKEY, name, surname, access_level, power_plant_code)



# --- Config ---
load_dotenv('./zadania/.config')
HUB_APIKEY = os.getenv("APIKEY")
LLM_APIKEY = os.getenv("LLM_APIKEY")
LLM_MODEL = "openai/gpt-5-mini"
HUB_BASE = "https://hub.ag3nts.org"
MAX_ITERATIONS = 15

# --- Suspects from previous task (S01E01 output) ---
SUSPECTS = [
    {"name": "Cezary",  "surname": "Żurek",   "born": 1987},
    {"name": "Jacek",   "surname": "Nowak",    "born": 1991},
    {"name": "Wojciech","surname": "Bielik",   "born": 1986},
    {"name": "Wacław",  "surname": "Jasiński", "born": 1986},
]

# ---------------------------------------------------------------------------
# Tool implementations (called by the agent when the LLM requests them)
# ---------------------------------------------------------------------------

# def get_power_plant_locations() -> list[dict]:
#     """Fetch list of nuclear power plants with codes and coordinates."""
#     url = f"{HUB_BASE}/data/{HUB_APIKEY}/findhim_locations.json"
#     resp = requests.get(url, timeout=10)
#     resp.raise_for_status()
#     return resp.json()


# def get_person_locations(name: str, surname: str) -> list[dict]:
#     """Fetch GPS coordinates where a person was spotted."""
#     payload = {"apikey": HUB_APIKEY, "name": name, "surname": surname}
#     resp = requests.post(f"{HUB_BASE}/api/location", json=payload, timeout=10)
#     resp.raise_for_status()
#     return resp.json()


# def get_access_level(name: str, surname: str, birth_year: int) -> int:
#     """Fetch the access level for a person."""
#     payload = {
#         "apikey": HUB_APIKEY,
#         "name": name,
#         "surname": surname,
#         "birthYear": int(birth_year),
#     }
#     resp = requests.post(f"{HUB_BASE}/api/accesslevel", json=payload, timeout=10)
#     resp.raise_for_status()
#     return resp.json()


# def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
#     """Return great-circle distance in kilometres between two points."""
#     R = 6371.0
#     phi1, phi2 = math.radians(lat1), math.radians(lat2)
#     dphi = math.radians(lat2 - lat1)
#     dlambda = math.radians(lon2 - lon1)
#     a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
#     return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# def find_closest_plant(person_locations: list[dict], plants: list[dict]) -> dict | None:
#     """
#     Return dict with 'plant' and 'distance_km' for the closest plant to any
#     of the person's locations.  Returns None if inputs are empty.
#     """
#     best = None
#     for loc in person_locations:
#         for plant in plants:
#             dist = haversine_km(
#                 loc["lat"], loc["lon"],
#                 plant["lat"], plant["lon"],
#             )
#             if best is None or dist < best["distance_km"]:
#                 best = {"plant": plant, "distance_km": dist, "location": loc}
#     return best


# def submit_answer(name: str, surname: str, access_level: int, power_plant_code: str) -> dict:
#     """Submit the final answer to /verify and return the hub response."""
#     payload = {
#         "apikey": HUB_APIKEY,
#         "task": "findhim",
#         "answer": {
#             "name": name,
#             "surname": surname,
#             "accessLevel": access_level,
#             "powerPlant": power_plant_code,
#         },
#     }
#     resp = requests.post(f"{HUB_BASE}/verify", json=payload, timeout=10)
#     resp.raise_for_status()
#     return resp.json()


# ---------------------------------------------------------------------------
# Tool registry — maps function names to callables + JSON-schema definitions
# ---------------------------------------------------------------------------

# TOOLS: list[dict] = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_power_plant_locations",
#             "description": "Fetch the list of nuclear power plants with their codes and GPS coordinates.",
#             "parameters": {"type": "object", "properties": {}, "required": []},
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_person_locations",
#             "description": "Fetch GPS coordinates where a specific suspect was spotted.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "name":    {"type": "string", "description": "First name"},
#                     "surname": {"type": "string", "description": "Last name"},
#                 },
#                 "required": ["name", "surname"],
#             },
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_access_level",
#             "description": "Fetch the security access level for a suspect.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "name":       {"type": "string"},
#                     "surname":    {"type": "string"},
#                     "birth_year": {"type": "integer", "description": "Year of birth as integer"},
#                 },
#                 "required": ["name", "surname", "birth_year"],
#             },
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "find_closest_plant",
#             "description": (
#                 "Given a list of person_locations and a list of plants "
#                 "(both already fetched), calculate which plant is closest."
#             ),
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "person_locations": {
#                         "type": "array",
#                         "items": {"type": "object"},
#                         "description": "List returned by get_person_locations",
#                     },
#                     "plants": {
#                         "type": "array",
#                         "items": {"type": "object"},
#                         "description": "List returned by get_power_plant_locations",
#                     },
#                 },
#                 "required": ["person_locations", "plants"],
#             },
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "submit_answer",
#             "description": "Submit the final answer to the verification endpoint.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "name":             {"type": "string"},
#                     "surname":          {"type": "string"},
#                     "access_level":     {"type": "integer"},
#                     "power_plant_code": {"type": "string", "description": "e.g. PWR1234PL"},
#                 },
#                 "required": ["name", "surname", "access_level", "power_plant_code"],
#             },
#         },
#     },
# ]

TOOL_MAP: dict[str, Any] = {
    "get_power_plant_locations": get_power_plant_locations,
    "get_person_locations":      get_person_locations,
    "get_access_level":          get_access_level,
    "find_closest_plant":        find_closest_plant,
    "submit_answer":             submit_answer,
    "geocode_city": lambda city_name, country="Poland": geocode_city(city_name, country),
}


# ---------------------------------------------------------------------------
# OpenRouter LLM call (with tool/function-calling support)
# ---------------------------------------------------------------------------

def call_llm(messages: list[dict], tools: list[dict] | None = None) -> dict:
    payload: dict = {"model": LLM_MODEL, "messages": messages}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {LLM_APIKEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = f"""You are a security investigation agent.
Your goal: identify which of the suspects was spotted near a nuclear power plant.

Suspects (name, surname, birth_year):
{json.dumps(SUSPECTS, ensure_ascii=False, indent=2)}

Steps you MUST follow:
1. Call get_power_plant_locations to get the plant list.
2. For EACH suspect call get_person_locations.
3. For EACH suspect call find_closest_plant (pass the fetched locations and plant list).
4. Identify the suspect with the shortest distance to any plant.
5. Call get_access_level for that suspect (use the birth_year from the suspects list).
6. Call submit_answer with all required fields.
7. Report the hub's response to the user.

IMPORTANT:
- Do not guess — always use the tool results.
- find_closest_plant requires BOTH person_locations AND plants — always pass both.
- Never call find_closest_plant with empty arguments.
- plants comes from the result of get_power_plant_locations.
- person_locations comes from the result of get_person_locations for that suspect.
"""


def run_agent() -> None:
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({"role": "user", "content": "Start the investigation."})

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- Iteration {iteration} ---")
        response = call_llm(messages, tools=TOOL_SCHEMAS)
        choice = response["choices"][0]
        msg = choice["message"]
        messages.append(msg)

        # If the model wants to call tools
        if choice["finish_reason"] == "tool_calls" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                fn_name = tc["function"]["name"]
                fn_args = json.loads(tc["function"]["arguments"])
                print(f"  Tool call: {fn_name}({fn_args})")

                try:
                    result = TOOL_MAP[fn_name](**fn_args)
                except Exception as exc:
                    result = {"error": str(exc)}

                print(f"  Result: {json.dumps(result, ensure_ascii=False)[:200]}...")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result, ensure_ascii=False),
                })
            continue  # feed results back to the model

        # Model finished without tool calls — print final answer
        print("\n=== Agent finished ===")
        print(msg.get("content", ""))
        break
    else:
        print("WARNING: Reached max iterations without a final answer.")


if __name__ == "__main__":
    run_agent()
