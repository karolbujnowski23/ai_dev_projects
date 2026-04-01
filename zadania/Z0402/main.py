import os
import asyncio
from dotenv import load_dotenv

from windpower.blackboard import Blackboard
from windpower.agents.action import ActionAgent
from windpower.agents.polling import PollingAgent
from windpower.agents.orchestrator import OrchestratorAgent
from windpower.utils.logger import logger

load_dotenv("../.config")

async def main():
    api_key = os.getenv("APIKEY")
    if not api_key:
        logger.error("APIKEY not found in environment. Testing with a dummy key for logging validation.")
        api_key = "test_key_123"

    openrouter_key = os.getenv("OPENROUTER_APIKEY", "")
    
    # 1. Initialize State
    blackboard = Blackboard(api_key, openrouter_key)
    
    # 2. Initialize Agents
    action_agent = ActionAgent(blackboard)
    polling_agent = PollingAgent(blackboard)
    orchestrator = OrchestratorAgent(blackboard, action_agent, polling_agent)
    
    # 3. Start Workflow
    await orchestrator.run()

if __name__ == "__main__":
    asyncio.run(main())
