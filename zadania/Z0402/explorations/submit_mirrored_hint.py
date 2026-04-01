import os
import asyncio
import aiohttp
from dotenv import load_dotenv

from windpower.utils.logger import logger

load_dotenv("../.config")

async def submit_final_hint():
    api_key = os.getenv("APIKEY")
    url = "https://hub.ag3nts.org/verify"
    
    hint = "Lustro czasu, lustro wiatru, bo wszystko jest zakodowanym lustrem"
    mirrored_hint = hint[::-1]
    
    logger.info(f"Mirrored hint to be submitted: {mirrored_hint}")
    
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
        start_resp = await session.post(url, json=start_payload)
        logger.info(f"Start response: {await start_resp.text()}")

        # Step 2: Queue a turbinecheck to satisfy the state machine
        logger.info("Queueing turbinecheck...")
        check_payload = {"apikey": api_key, "task": "windpower", "answer": {"action": "get", "param": "turbinecheck"}}
        await session.post(url, json=check_payload)
        await asyncio.sleep(0.1) # Brief pause to ensure it's sent

        # Step 3: Submit the final answer
        logger.info("Submitting the final mirrored hint payload...")
        final_resp = await session.post(url, json=final_payload)
        
        logger.info("Final API Response:")
        print(await final_resp.text())

if __name__ == "__main__":
    asyncio.run(submit_final_hint())
