import asyncio
import os
import aiohttp
from dotenv import load_dotenv
import json

from windpower.utils.logger import logger

load_dotenv("../.config")

async def gamble_for_flag():
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

    for i in range(1, 6): # Try up to 5 times
        logger.info(f"--- Attempt {i}/5 ---")
        async with aiohttp.ClientSession() as session:
            try:
                # Step 1: Start
                await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "start"}})
                
                # Step 2: Turbine Check
                await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "get", "param": "turbinecheck"}})

                # Step 3: Submit Answer
                final_resp = await session.post(url, json=final_payload)
                
                text = await final_resp.text()
                logger.info(f"Attempt {i} Response: {text}")

                # Check for success
                if "FLG" in text or "flag" in text.lower() or '"code": 0' in text:
                    logger.info("SUCCESS! Flag received.")
                    print(text)
                    break
                
            except Exception as e:
                logger.error(f"Attempt {i} failed with exception: {e}")
        
        await asyncio.sleep(2) # Wait 2 seconds before next attempt

if __name__ == "__main__":
    asyncio.run(gamble_for_flag())
