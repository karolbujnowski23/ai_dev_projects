import aiohttp
import asyncio
import json
from typing import Dict, Any
from windpower.utils.logger import logger
from windpower.blackboard import Blackboard

class ActionAgent:
    def __init__(self, blackboard: Blackboard):
        self.blackboard = blackboard

    async def _send_request(self, payload: Dict[str, Any]):
        """Internal method to fire a fire-and-forget POST to the API."""
        async with aiohttp.ClientSession() as session:
            try:
                # We do not wait for the result here, as the API queues it
                # and we rely on the PollingAgent to catch it.
                logger.info(f"ActionAgent: Sending -> {payload.get('answer', {}).get('action', 'Unknown Action')}")
                async with session.post(self.blackboard.base_url, json=payload, timeout=5) as response:
                    text = await response.text()
                    if response.status not in [200, 201, 202]:
                         logger.error(f"ActionAgent: Error queuing {payload.get('answer', {}).get('action')}: {response.status} - {text}")
                    else:
                         try:
                             data = json.loads(text)
                             logger.debug(f"ActionAgent: Sync Response -> {text}")
                             # If it's a real response (not just queued), we might want to handle it
                             if data.get("code") != 11 and "queued" not in str(data.get("message", "")).lower():
                                 from windpower.agents.polling import PollingAgent
                                 # We can't easily call PollingAgent here directly if we don't have it,
                                 # but we can push to blackboard or log it.
                                 logger.info(f"ActionAgent: Got sync response: {data}")
                         except json.JSONDecodeError:
                             pass
            except Exception as e:
                logger.error(f"ActionAgent: Exception sending request: {e}")

    async def fire_action(self, action_name: str, **kwargs):
        """Builds the JSON payload and fires it."""
        payload = {
            "apikey": self.blackboard.api_key,
            "task": "windpower",
            "answer": {
                "action": action_name
            }
        }
        # Add any extra parameters (like 'configs' or 'startDate') to 'answer'
        if kwargs:
            payload["answer"].update(kwargs)
            
        await self._send_request(payload)

    async def fire_concurrent_actions(self, actions: list[tuple[str, dict]]):
        """Fires multiple actions at once."""
        tasks = [self.fire_action(action[0], **action[1]) for action in actions]
        await asyncio.gather(*tasks)
