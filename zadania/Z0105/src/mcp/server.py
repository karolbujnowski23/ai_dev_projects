# -*- coding: utf-8 -*-

import httpx
import asyncio
import time
from src.config import API_KEY, LLM_API_KEY
from src.helpers.logger import log

HUB_URL = "https://hub.ag3nts.org/verify"

async def call_railway_api(answer_payload: dict):
    """
    Call the Railway API with 503 retry and rate limiting logic.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            try:
                log.info(f"Sending request: {answer_payload}")
                response = await client.post(HUB_URL, json={
                    "apikey": API_KEY,
                    "task": "railway",
                    "answer": answer_payload
                })
                
                # Check for rate limits in headers
                # remaining = response.headers.get("x-ratelimit-remaining")
                # reset = response.headers.get("x-ratelimit-reset")
                # if remaining and int(remaining) <= 1:
                #     wait_time = int(reset) if reset else 2
                #     log.info(f"⚠️ Rate limit reached. Sleeping for {wait_time}s...")
                #     await asyncio.sleep(wait_time)

                if response.status_code == 503:
                    log.info("⚠️ Server 503 (Overloaded). Retrying in 2s...")
                    await asyncio.sleep(2)
                    continue
                
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        retry_after = error_data.get("retry_after", 0)
                        penalty = error_data.get("penalty_seconds", 0)
                        
                        if retry_after > 0:
                            wait_time = retry_after + penalty
                            
                            if wait_time > 240:
                                log.error(f"❌ WAIT TIME TOO LONG ({wait_time}s > 240s). Stopping.")
                                return {"error": "WAIT_TIME_EXCEEDED", "wait_time": wait_time, "message": error_data.get('message')}

                            log.error(f"❌ API Error ({response.status_code}): {error_data.get('message')}")
                            log.info(f"⏳ Respektuję limit: Czekam {wait_time}s (retry_after: {retry_after} + penalty: {penalty})...")
                            await asyncio.sleep(wait_time)
                            continue
                    except Exception:
                        pass

                    log.error(f"API Error ({response.status_code}): {response.text}")
                    log.info("⚠️ Nieoczekiwany błąd. Zatrzymuję ze względu na ryzyko długiego oczekiwania.")
                    return {"error": "UNEXPECTED_ERROR", "status": response.status_code, "text": response.text}
                
                result = response.json()
                log.success(f"API Success: {result}")
                
                # Manual sleep to be safe with rate limits
                await asyncio.sleep(1)
                
                return result
            except Exception as e:
                log.error(f"Network error: {e}. Stopping.")
                return {"error": "NETWORK_ERROR", "message": str(e)}

# Tool definitions that agent will call
async def get_help():
    """Get documentation for the railway API."""
    return await call_railway_api({"action": "help"})

async def reconfigure(route: str):
    """Start reconfiguration for a specific route."""
    return await call_railway_api({"action": "reconfigure", "route": route})

async def set_status(route: str, value: str):
    """Set the status for a route (e.g. RTOPEN, RTCLOSE)."""
    return await call_railway_api({"action": "setstatus", "route": route, "value": value})

async def save(route: str):
    """Save changes for a route."""
    return await call_railway_api({"action": "save", "route": route})

async def get_status(route: str):
    """Check current status of a route."""
    return await call_railway_api({"action": "getstatus", "route": route})
