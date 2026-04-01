import asyncio
from typing import List

from windpower.utils.logger import logger
from windpower.blackboard import Blackboard
from windpower.agents.action import ActionAgent
from windpower.agents.polling import PollingAgent
from windpower.agents.intelligence import IntelligenceAgent
from windpower.agents.crypto import CryptographyAgent

class OrchestratorAgent:
    def __init__(self, blackboard: Blackboard, action_agent: ActionAgent, polling_agent: PollingAgent):
        self.blackboard = blackboard
        self.action = action_agent
        self.polling = polling_agent
        self.intelligence = IntelligenceAgent(self.blackboard)
        self.crypto = CryptographyAgent(self.blackboard, self.action)
        
    async def run(self):
        """The main 40-second state machine loop."""
        logger.info("Orchestrator: Starting the Windpower Task (40s limit).")
        
        # 1. Start the listener
        await self.polling.start()
        
        # 2. Open Window
        await self.action.fire_action("start")
        await asyncio.sleep(0.5) # Slight pause to let start fully register
        
        # 3. Request data directly
        logger.info("Orchestrator: Firing data requests (weather, turbinecheck, powerplantcheck).")
        await self.action.fire_concurrent_actions([
            ("get", {"param": "weather"}),
            ("get", {"param": "turbinecheck"}),
            ("get", {"param": "powerplantcheck"})
        ])
        
        # Wait for all data to arrive (Timeout 25s)
        try:
            await asyncio.wait_for(self.blackboard.wait_for("data_gathered"), timeout=25.0)
            logger.info("Orchestrator: All raw data gathered. Triggering Intelligence Agent.")
        except asyncio.TimeoutError:
            logger.error("Orchestrator: Timed out waiting for Weather, State, and Deficit. Aborting.")
            self.polling.stop()
            return
            
        # 4. Intelligence Agent creates schedule
        await self.intelligence.calculate_schedule()
        
        if not self.blackboard.data.get("draft_schedule"):
            logger.error("Orchestrator: Failed to draft schedule. Aborting.")
            self.polling.stop()
            return
            
        # 5. Crypto Agent fetches unlock codes
        await self.crypto.fetch_unlock_codes()
        
        try:
            await asyncio.wait_for(self.blackboard.wait_for("unlock_codes_ready"), timeout=10.0)
            logger.info("Orchestrator: All unlock codes gathered.")
        except asyncio.TimeoutError:
            logger.error("Orchestrator: Timed out waiting for unlock codes. Aborting.")
            self.polling.stop()
            return
            
        # 6. Apply codes and configure
        self.crypto.sign_schedule()
        
        final_configs = self.blackboard.data.get("final_configs")
        if not final_configs:
            logger.error("Orchestrator: Final configs are empty. Aborting.")
            self.polling.stop()
            return
            
        # 7. Configure schedule
        # The docs say: 'config': {'requiredSingle': ['startDate', 'startHour', 'pitchAngle', 'turbineMode', 'unlockCode'], 'requiredBatch': ['configs'], ...
        # But earlier, the Z0402text.md said:
        # "answer": {
        #    "action": "config",
        #    "configs": {
        #       "2026-03-24 20:00:00": { "pitchAngle": 45, "turbineMode": "production", "unlockCode": "..." }
        #    }
        # }
        logger.info(f"Orchestrator: Sending configs -> {final_configs}")
        await self.action.fire_action("config", configs=final_configs)
        await asyncio.sleep(0.5) # Let it register
        
        # 8. Turbinecheck (required before done)
        await self.action.fire_action("get", param="turbinecheck")
        
        try:
            await asyncio.wait_for(self.blackboard.wait_for("turbinecheck_ok"), timeout=5.0)
            logger.info("Orchestrator: Turbinecheck OK.")
        except asyncio.TimeoutError:
            logger.warning("Orchestrator: Turbinecheck didn't return OK explicitly, proceeding anyway.")
            
        # 9. Done!
        await self.action.fire_action("done")
        
        try:
            await asyncio.wait_for(self.blackboard.wait_for("done_flag_received"), timeout=10.0)
            logger.info("Orchestrator: Done flag received! Task completed successfully.")
        except asyncio.TimeoutError:
            logger.error("Orchestrator: Timed out waiting for final flag.")
            
        self.polling.stop()
