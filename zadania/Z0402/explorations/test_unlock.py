import asyncio
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv("../.config")

async def test_unlock():
    api_key = os.getenv("APIKEY")
    url = "https://hub.ag3nts.org/verify"
    
    async with aiohttp.ClientSession() as session:
        # 1. start
        await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "start"}})
        
        # 2. queue unlock code
        payload = {
            "apikey": api_key, 
            "task": "windpower", 
            "answer": {
                "action": "unlockCodeGenerator",
                "startDate": "2026-04-02",
                "startHour": "18:00:00",
                "windMs": 25.0,
                "pitchAngle": 90
            }
        }
        await session.post(url, json=payload)
        
        # 3. poll
        for _ in range(15):
            await asyncio.sleep(1)
            resp = await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "getResult"}})
            text = await resp.text()
            if "No completed queued" not in text:
                 print(text)

if __name__ == "__main__":
    asyncio.run(test_unlock())
