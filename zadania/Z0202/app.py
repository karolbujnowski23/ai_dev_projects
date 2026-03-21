import asyncio
from src.mcp.server import mcp_server
from src.helpers.logger import log
from src.agent import Agent

async def async_main():
    """
    Entry point for the standalone Agent solving Z0202.
    """
    agent = Agent()
    await agent.run("electricity")

def main():
    """
    Uruchamia Agenta do rozwiązania zadania.
    """
    log.info("Starting Z0202 Electricity Agent...")
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
