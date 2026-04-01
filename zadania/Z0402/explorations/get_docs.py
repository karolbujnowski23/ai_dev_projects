import asyncio
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv("../.config")

async def get_docs():
    api_key = os.getenv("APIKEY")
    url = "https://hub.ag3nts.org/verify"
    
    async with aiohttp.ClientSession() as session:
        # 1. start
        await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "start"}})
        
        # 2. get doc
        resp = await session.post(url, json={"apikey": api_key, "task": "windpower", "answer": {"action": "get", "param": "documentation"}})
        print(await resp.text())

if __name__ == "__main__":
    asyncio.run(get_docs())
