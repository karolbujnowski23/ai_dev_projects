import aiohttp
import asyncio
import json
from typing import Dict, Any, List
from windpower.utils.logger import logger
from windpower.blackboard import Blackboard

class PollingAgent:
    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard
        self._running = False
        self._poll_interval = 0.5  # Check every 500ms

    async def start(self):
        self._running = True
        logger.info("PollingAgent: Started listening on getResult loop.")
        asyncio.create_task(self._poll_loop())

    def stop(self):
        self._running = False
        logger.info("PollingAgent: Stopped.")

    async def _poll_loop(self):
        async with aiohttp.ClientSession() as session:
            while self._running:
                payload = {
                    "apikey": self.blackboard.api_key,
                    "task": "windpower",
                    "answer": {
                        "action": "getResult"
                    }
                }
                
                try:
                    async with session.post(self.blackboard.base_url, json=payload, timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data:
                                # We caught a response from the queue!
                                logger.debug(f"PollingAgent: Received Raw JSON -> {json.dumps(data)}")
                                await self._handle_incoming_data(data)
                        elif response.status == 429:
                            # Rate limit hit, back off slightly
                            await asyncio.sleep(1)
                        else:
                            # 404 or other means queue is likely empty, or we hit a true error
                            pass
                except asyncio.TimeoutError:
                    # Ignore timeouts, just loop again
                    pass
                except Exception as e:
                    logger.error(f"PollingAgent: Polling Exception: {e}")
                
                await asyncio.sleep(self._poll_interval)

    async def _handle_incoming_data(self, data: Dict[str, Any]):
        """Parses the random JSON response and updates the Blackboard state machine."""
        
        message = str(data.get("message", ""))
        code = data.get("code")

        # Handle pending queue items explicitly
        if code == 11 or "No completed queued response is available yet" in message:
            return  # Just keep polling

        # 1. Catching 'help' response
        if "available endpoints" in message.lower() or "functions" in message.lower() or isinstance(data.get("endpoints"), list):
             logger.info("PollingAgent: Caught 'help' response. Extracting endpoints.")
             # Assume endpoints are returned in a list or dict. 
             # We must extract the exact strings to call next.
             # e.g., "endpoints": {"weather": "getWeather", "turbine": "turbineStatus", "power": "powerRequirements"}
             if "endpoints" in data:
                 self.blackboard.data["endpoints"] = data["endpoints"]
                 self.blackboard.set_event("help_received")
             elif "message" in data:
                 # If endpoints are just in message, we might need to parse it later, 
                 # but for now let's save the raw data
                 self.blackboard.data["endpoints_raw"] = data
                 self.blackboard.set_event("help_received")
                 
        source = data.get("sourceFunction", "")

        # 2. Catching Data (Weather/State/Deficit)
        if source == "weather":
            logger.info("PollingAgent: Caught Weather Data.")
            self.blackboard.data["weather"] = data
            self._check_data_gathered()
            
        elif source == "turbinecheck":
             # Note: we might receive this before "done". If we do, set the OK flag if code is 0
             logger.info("PollingAgent: Caught Turbine State Data.")
             self.blackboard.data["turbine_state"] = data
             self._check_data_gathered()
             if data.get("code") == 0 or "ok" in str(data).lower():
                 self.blackboard.set_event("turbinecheck_ok")
             
        elif source == "powerplantcheck":
             logger.info("PollingAgent: Caught Power Deficit Data.")
             self.blackboard.data["power_deficit"] = data
             self._check_data_gathered()
             
        # 3. Catching Unlock Codes
        elif "unlockCode" in data or "unlockCodeGenerator" in str(data.get("sourceFunction", "")):
             logger.info("PollingAgent: Caught Unlock Code.")
             sp = data.get("signedParams", {})
             timestamp = f"{sp.get('startDate', '')} {sp.get('startHour', '')}".strip()
             if not timestamp:
                 timestamp = str(len(self.blackboard.data["unlock_codes"]))
                 
             code_val = data.get("unlockCode")
             self.blackboard.data["unlock_codes"][timestamp] = code_val
             
             # If we have all codes for our draft schedule, set event
             if self.blackboard.data["draft_schedule"] and len(self.blackboard.data["unlock_codes"]) == len(self.blackboard.data["draft_schedule"]):
                 self.blackboard.set_event("unlock_codes_ready")
                 
        # 4. Catching Turbinecheck success (if separate)
        elif "turbinecheck" in str(data).lower() and ("ok" in str(data).lower() or "success" in str(data).lower() or data.get("code") == 0):
             logger.info("PollingAgent: Caught turbinecheck success via catchall.")
             self.blackboard.set_event("turbinecheck_ok")
             
        # 5. Catching the Final Flag (from 'done')
        elif "FLAG" in str(data) or "{{" in str(data) or "flag" in data:
             logger.info(f"PollingAgent: *** FLAG CAUGHT *** -> {data}")
             self.blackboard.data["flag"] = data
             self.blackboard.set_event("done_flag_received")
             self.stop()
             
        # 6. Error handling
        elif code and int(code) != 0:
             logger.error(f"PollingAgent: API Error Caught: {data}")
             
    def _check_data_gathered(self):
        """Checks if all three essential data pieces have arrived."""
        d = self.blackboard.data
        if d["weather"] and d["turbine_state"] and d["power_deficit"]:
            logger.info("PollingAgent: All necessary data gathered (Weather, State, Deficit). Signaling Orchestrator.")
            self.blackboard.set_event("data_gathered")
