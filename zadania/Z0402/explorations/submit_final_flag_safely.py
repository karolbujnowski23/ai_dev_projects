import asyncio
import os
import aiohttp
from dotenv import load_dotenv
from datetime import datetime, timezone

from windpower.utils.logger import logger

load_dotenv("../.config")

async def submit_final_flag_safely():
    api_key = os.getenv("APIKEY")
    url = "https://hub.ag3nts.org/verify"
    
    hint = "Lustro czasu, lustro wiatru, bo wszystko jest zakodowanym lustrem"
    mirrored_hint = hint[::-1]
    
    async with aiohttp.ClientSession() as session:
        # === Step 1: Start a new session ===
        logger.info("Opening service window...")
        await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "start"}})

        # === Step 2: Generate an unlock code for a safe, immediate config ===
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")
        # The API requires HH:00:00 format, so we use the current hour.
        hour_str = now.strftime("%H:00:00")
        
        logger.info(f"Requesting unlock code for a safe config at {today_str} {hour_str}...")
        safe_config_params = {
            "startDate": today_str,
            "startHour": hour_str,
            "windMs": 0, # Assume no wind for safety
            "pitchAngle": 90 # Safe angle
        }
        await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "unlockCodeGenerator", **safe_config_params}})
        
        # Poll for the unlock code
        safe_unlock_code = None
        for _ in range(10):
            await asyncio.sleep(1)
            resp = await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "getResult"}})
            data = await resp.json()
            if data.get("sourceFunction") == "unlockCodeGenerator":
                safe_unlock_code = data.get("unlockCode")
                logger.info(f"Got safe unlock code: {safe_unlock_code}")
                break
        
        if not safe_unlock_code:
            logger.error("Failed to get safe unlock code. Aborting.")
            return

        # === Step 3: Send the safe configuration ===
        logger.info("Sending safe config to protect the turbine...")
        full_safe_config = {
            "pitchAngle": 90,
            "turbineMode": "idle",
            "unlockCode": safe_unlock_code
        }
        config_payload = {
            "apikey": api_key,
            "task": "windpower",
            "answer": {
                "action": "config",
                "configs": {f"{today_str} {hour_str}": full_safe_config}
            }
        }
        await session.post(url, json=config_payload)
        await asyncio.sleep(0.5) # Let config register

        # === Step 4: Run the required turbine check ===
        logger.info("Queueing turbinecheck...")
        await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "get", "param": "turbinecheck"}})
        await asyncio.sleep(0.5)

        # === Step 5: Submit the final answer ===
        logger.info("Submitting the final mirrored hint payload...")
        final_payload = {
            "apikey": api_key,
            "task": "windpower",
            "answer": {
                "action": "done",
                "answer": mirrored_hint
            }
        }
        final_resp = await session.post(url, json=final_payload)
        
        logger.info("Final API Response:")
        print(await final_resp.text())

if __name__ == "__main__":
    asyncio.run(submit_final_flag_safely())
