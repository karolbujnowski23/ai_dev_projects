import asyncio
from typing import Dict, Any, List, Optional

class Blackboard:
    def __init__(self, api_key: str, openrouter_key: str):
        self.api_key = api_key
        self.openrouter_key = openrouter_key
        self.base_url = "https://hub.ag3nts.org/verify"
        
        # Events to signal phase completion
        self.events = {
            "help_received": asyncio.Event(),
            "data_gathered": asyncio.Event(),
            "schedule_drafted": asyncio.Event(),
            "unlock_codes_ready": asyncio.Event(),
            "turbinecheck_ok": asyncio.Event(),
            "done_flag_received": asyncio.Event(),
        }
        
        # Shared State Data
        self.data: Dict[str, Any] = {
            "endpoints": {},      # Discovered from /help
            "weather": None,
            "turbine_state": None,
            "power_deficit": None,
            "draft_schedule": None, # From LLM
            "unlock_codes": {},   # Dict mapping timestamp -> code
            "final_configs": None, # Fully signed schedule ready for /config
            "flag": None          # The final answer
        }

    def set_event(self, event_name: str):
        if event_name in self.events:
            self.events[event_name].set()

    def wait_for(self, event_name: str):
        if event_name in self.events:
            return self.events[event_name].wait()
        raise ValueError(f"Event {event_name} not found.")
