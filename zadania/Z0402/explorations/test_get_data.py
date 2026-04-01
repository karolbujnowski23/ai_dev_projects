import asyncio
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv("../.config")

async def test_get_data():
    api_key = os.getenv("APIKEY")
    url = "https://hub.ag3nts.org/verify"
    
    async with aiohttp.ClientSession() as session:
        # 1. start
        await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "start"}})
        
        # 2. queue weather and powerplantcheck
        await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "get", "param": "weather"}})
        await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "get", "param": "powerplantcheck"}})
        
        # 3. poll for results
        for _ in range(30):
            await asyncio.sleep(1)
            resp = await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "getResult"}})
            text = await resp.text()
            if "No completed queued" not in text:
                 print(text)

if __name__ == "__main__":
    asyncio.run(test_get_data())
