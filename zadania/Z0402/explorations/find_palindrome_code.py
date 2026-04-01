import asyncio
import os
import aiohttp
from dotenv import load_dotenv
import math

from windpower.utils.logger import logger

load_dotenv("../.config")

def chunk_list(data, size):
    return [data[i:i + size] for i in range(0, len(data), size)]

async def find_palindrome_code():
    api_key = os.getenv("APIKEY")
    url = "https://hub.ag3nts.org/verify"
    
    weather_data = None
    
    # === Step 1: Get Weather Data Once ===
    async with aiohttp.ClientSession() as session:
        logger.info("Starting a temporary session to fetch weather data...")
        await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "start"}})
        await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "get", "param": "weather"}})
        
        for _ in range(35):
            await asyncio.sleep(1)
            resp = await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "getResult"}})
            try:
                data = await resp.json()
                if data.get("sourceFunction") == "weather":
                    weather_data = data
                    logger.info("Weather data received.")
                    break
            except Exception: pass
    
    if not weather_data:
        logger.error("Failed to retrieve weather data. Aborting search.")
        return

    # === Step 2: Create All Combinations and Batches ===
    combinations = []
    for point in weather_data["forecast"]:
        for pitch in [0, 45, 90]:
            combinations.append({
                "startDate": point["timestamp"].split(" ")[0],
                "startHour": point["timestamp"].split(" ")[1],
                "windMs": float(point["windMs"]),
                "pitchAngle": pitch
            })
            
    BATCH_SIZE = 30
    batches = chunk_list(combinations, BATCH_SIZE)
    logger.info(f"Created {len(combinations)} combinations, split into {len(batches)} batches of size {BATCH_SIZE}.")
    
    found_code = None

    # === Step 3: Process Each Batch in a New Session ===
    for i, batch in enumerate(batches):
        if found_code: break
        
        logger.info(f"--- Starting Batch {i+1}/{len(batches)} ---")
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "start"}})
            
            # Queue requests for the current batch
            tasks = [session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "unlockCodeGenerator", **combo}}) for combo in batch]
            await asyncio.gather(*tasks)
            logger.info(f"Queued {len(batch)} requests for this batch.")

            # Poll for results
            for _ in range(40): # Poll for up to 35-40s
                await asyncio.sleep(0.8) # A slightly less aggressive poll
                resp = await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "getResult"}})
                try:
                    data = await resp.json()
                    if data.get("sourceFunction") == "unlockCodeGenerator":
                        code = data.get("unlockCode")
                        if code and code.lower() == code.lower()[::-1]: # Case-insensitive check
                            logger.info(f"PALINDROME FOUND! Code: {code}, Params: {data.get('signedParams')}")
                            found_code = code
                            break
                except Exception: pass
            
            if found_code:
                break

    # === Step 4: Submit the Final Answer ===
    if not found_code:
        logger.error("Brute-force search completed, but no palindrome code was found.")
        return
        
    async with aiohttp.ClientSession() as session:
        logger.info(f"Submitting palindrome code '{found_code}' as the answer...")
        final_payload = {"apikey": api_key, "task": "windpower", "answer": found_code}
        final_resp = await session.post(url, json=final_payload)
        logger.info("Final API Response:")
        print(await final_resp.text())

if __name__ == "__main__":
    asyncio.run(find_palindrome_code())
