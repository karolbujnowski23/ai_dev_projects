import asyncio
import os
import aiohttp
from dotenv import load_dotenv

from windpower.utils.logger import logger

load_dotenv("../.config")

async def submit_final_flag_pacification():
    api_key = os.getenv("APIKEY")
    url = "https://hub.ag3nts.org/verify"
    
    hint = "Lustro czasu, lustro wiatru, bo wszystko jest zakodowanym lustrem"
    mirrored_hint = hint[::-1]
    
    final_payload = {
        "apikey": api_key,
        "task": "windpower",
        "answer": {
            "action": "done",
            "answer": mirrored_hint
        }
    }

    async with aiohttp.ClientSession() as session:
        # Step 1: Start the service window
        logger.info("Opening service window with 'start'...")
        start_payload = {"apikey": api_key, "task": "windpower", "answer": {"action": "start"}}
        await session.post(url, json=start_payload)
        
        # Step 2: Perform a harmless, synchronous action to pacify the state machine
        logger.info("Performing harmless 'get(documentation)' action...")
        doc_payload = {"apikey": api_key, "task": "windpower", "answer": {"action": "get", "param": "documentation"}}
        await session.post(url, json=doc_payload)

        # Step 3: Submit the final answer
        logger.info("Submitting the final mirrored hint payload...")
        final_resp = await session.post(url, json=final_payload)
        
        logger.info("Final API Response:")
        print(await final_resp.text())

if __name__ == "__main__":
    asyncio.run(submit_final_flag_pacification())
