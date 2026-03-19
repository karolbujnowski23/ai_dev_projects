# -*- coding: utf-8 -*-

import asyncio
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import run_agent
from src.helpers.logger import log

async def main():
    log.box("Railway System Activation Agent (GPT-5 Nano)")
    
    query = """ZADANIE:
Aktywuj trasę kolejową X-01 (ustaw status na RTOPEN).
1. Zacznij od pobrania instrukcji (get_help).
2. Przeprowadź cały proces zgodnie z instrukcją API.
3. Znajdź i zbierz DWIE różne flagi w formacie {FLG:...}. Nie przerywaj po pierwszej.
4. Jeśli czas oczekiwania przekroczy 4 minuty, system sam przerwie działanie błędem WAIT_TIME_EXCEEDED."""
    
    try:
        result = await run_agent(query)
        log.success(f"Final response: {result}")
    except Exception as e:
        log.error(f"Execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
