# -*- coding: utf-8 -*-

import asyncio
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import run_agent
from src.helpers.logger import log
from src.config import API_CONFIG, LLM_API_KEY, API_KEY

async def main():
    log.info(f"DEBUG: LLM_API_KEY length: {len(LLM_API_KEY)}")
    log.info(f"DEBUG: API_KEY length: {len(API_KEY)}")
    log.box("Transport Declaration Agent - Gdańsk to Żarnowiec")
    
    query = """DANE DO PRZESYŁKI:
Nadawca: 450202122
Punkt nadawczy: Gdańsk
Punkt docelowy: Żarnowiec
Waga: 2800 kg (2,8 t)
Budżet: 0 PP
Zawartość: kasety z paliwem do reaktora
Uwagi specjalne: brak

ZADANIE:
Znajdź wzór deklaracji w dokumentacji, ustal kod trasy, oblicz koszt/wybierz darmową kategorię, wypełnij deklarację i wyślij do weryfikacji."""
    
    try:
        result = await run_agent(query)
        log.success(f"Final response: {result}")
    except Exception as e:
        log.error(f"Execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
