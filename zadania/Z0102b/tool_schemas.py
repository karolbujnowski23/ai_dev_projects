"""
tool_schemas.py — JSON Schema definitions for all LLM function-calling tools.

Import TOOL_SCHEMAS into agent.py and pass it as the `tools` parameter
when calling the LLM API.
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "geocode_city",
            "description": "Estimate GPS coordinates for a Polish city by name using OpenStreetMap.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_name": {"type": "string", "description": "City name in Polish, e.g. 'Zabrze'"},
                    "country":   {"type": "string", "default": "Poland"},
                },
                "required": ["city_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_power_plant_locations",
            "description": (
                "Fetch the list of nuclear power plants from the hub. "
                "Returns a list of dicts with 'code', 'lat', 'lon' and possibly other fields."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_person_locations",
            "description": "Fetch all GPS coordinates where a specific suspect was spotted.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":    {"type": "string", "description": "Suspect's first name"},
                    "surname": {"type": "string", "description": "Suspect's last name"},
                },
                "required": ["name", "surname"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_access_level",
            "description": "Fetch the security access level for a suspect.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":       {"type": "string"},
                    "surname":    {"type": "string"},
                    "birth_year": {
                        "type": "integer",
                        "description": "Year of birth as an integer, e.g. 1987",
                    },
                },
                "required": ["name", "surname", "birth_year"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_closest_plant",
            "description": (
                "Given already-fetched person_locations and plants lists, "
                "compute which plant is closest and return the plant dict with distance_km."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "person_locations": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Output of get_person_locations for ONE suspect",
                    },
                    "plants": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Output of get_power_plant_locations",
                    },
                },
                "required": ["person_locations", "plants"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_answer",
            "description": "Submit the final answer to /verify and return the hub response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name":             {"type": "string"},
                    "surname":          {"type": "string"},
                    "access_level":     {"type": "integer"},
                    "power_plant_code": {
                        "type": "string",
                        "description": "Power plant code, e.g. PWR1234PL",
                    },
                },
                "required": ["name", "surname", "access_level", "power_plant_code"],
            },
        },
    },
]
