import asyncio
import os
import aiohttp
from dotenv import load_dotenv

from windpower.utils.logger import logger

load_dotenv("../.config")

async def get_mirror_flag():
    api_key = os.getenv("APIKEY")
    url = "https://hub.ag3nts.org/verify"
    
    # 1. Base data from the first storm
    base_data = {
        "startDate": "2026-04-02",
        "startHour": "18:00:00",
        "windMs": 25.0,
        "pitchAngle": 90
    }
    logger.info(f"Base data: {base_data}")

    # 2. Mirror the NUMERIC values, keeping date/time intact.
    mirrored_data = {
        "startDate": base_data["startDate"],
        "startHour": base_data["startHour"],
        "windMs": float(str(base_data["windMs"])[::-1]),
        "pitchAngle": int(str(base_data["pitchAngle"])[::-1])
    }
    logger.info(f"Mirrored data for unlockCodeGenerator: {mirrored_data}")

    async with aiohttp.ClientSession() as session:
        # Open a new service window
        await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "start"}})
        
        # 3. Queue the request for a "mirrored" unlock code
        payload = {
            "apikey": api_key,
            "task": "windpower",
            "answer": {"action": "unlockCodeGenerator", **mirrored_data}
        }
        await session.post(url, json=payload)
        logger.info("Request for mirrored unlock code has been queued.")
        
        # 4. Poll for the result
        mirrored_code = None
        for i in range(30): # Poll for up to 30 seconds
            await asyncio.sleep(1)
            resp = await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "getResult"}})
            try:
                data = await resp.json()
                logger.debug(f"Polling... got: {data}") # Log every response
                if data.get("sourceFunction") == "unlockCodeGenerator":
                    mirrored_code = data.get("unlockCode")
                    logger.info(f"Successfully retrieved mirrored unlock code: {mirrored_code}")
                    break
            except Exception:
                continue
        
        if not mirrored_code:
            logger.error("Failed to retrieve mirrored unlock code.")
            return

        # 5. Submit the mirrored code as the answer
        logger.info(f"Submitting mirrored code '{mirrored_code}' as the answer...")
        final_payload = {
            "apikey": api_key,
            "task": "windpower",
            "answer": mirrored_code
        }
        final_resp = await session.post(url, json=final_payload)
        
        logger.info("Final API Response:")
        try:
            print(await final_resp.text())
        except Exception as e:
            logger.error(f"Error printing final response: {e}")


if __name__ == "__main__":
    asyncio.run(get_mirror_flag())
