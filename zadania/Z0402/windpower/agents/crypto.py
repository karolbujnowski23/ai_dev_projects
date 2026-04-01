import asyncio
from typing import Dict, Any

from windpower.utils.logger import logger
from windpower.blackboard import Blackboard
from windpower.agents.action import ActionAgent

class CryptographyAgent:
    def __init__(self, blackboard: Blackboard, action_agent: ActionAgent):
        self.blackboard = blackboard
        self.action = action_agent

    async def fetch_unlock_codes(self):
        """Requests unlock codes for all drafted schedule points."""
        schedule = self.blackboard.data.get("draft_schedule")
        if not schedule:
            logger.error("CryptographyAgent: No draft schedule found.")
            return

        logger.info(f"CryptographyAgent: Requesting unlock codes for {len(schedule)} timestamps.")
        
        # Fire requests for every timestamp in the schedule concurrently
        for timestamp, config in schedule.items():
            # timestamp is "YYYY-MM-DD HH:MM:SS"
            date_part, time_part = timestamp.split(" ")
            
            wind_ms = config.get("windMs", 0)
            
            payload = {
                "startDate": date_part,
                "startHour": time_part,
                "windMs": wind_ms, 
                "pitchAngle": config["pitchAngle"]
            }
            
            # The API doesn't accept extra fields, so we just use the kwargs
            await self.action.fire_action("unlockCodeGenerator", **payload)
            
        logger.info("CryptographyAgent: All unlock code requests fired.")

    def sign_schedule(self):
        """Applies received unlock codes to the schedule."""
        schedule = self.blackboard.data.get("draft_schedule") or {}
        codes = self.blackboard.data.get("unlock_codes") or {}
        
        final_configs = {}
        
        for ts, config in schedule.items():
            date_part, time_part = ts.split(" ")
            
            # The polling agent saves it as "{startDate} {startHour}"
            # which matches `ts` perfectly!
            code = codes.get(ts)
            
            if not code:
                logger.error(f"CryptographyAgent: Missing unlock code for timestamp {ts}")
                continue
                
            final_configs[ts] = {
                 "pitchAngle": config["pitchAngle"],
                 "turbineMode": config["turbineMode"],
                 "unlockCode": code
            }
            
        self.blackboard.data["final_configs"] = final_configs
        logger.info(f"CryptographyAgent: Successfully signed {len(final_configs)} configurations.")
