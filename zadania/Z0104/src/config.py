# -*- coding: utf-8 -*-

#   config.py

import os
from pathlib import Path

# Try to find .config in current dir, parent, or 2 levels up
def find_config():
    paths = [
        Path(".config"),
        Path("..") / ".config",
        Path("../..") / ".config",
        Path(__file__).parent.parent.parent / ".config",
        Path(__file__).parent.parent.parent.parent / ".config"
    ]
    for p in paths:
        if p.exists():
            return p
    return None

CONFIG_PATH = find_config()

def load_config(path: Path):
    config = {}
    if path and path.exists():
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip().strip('"').strip("'")
    return config

CUSTOM_CONFIG = load_config(CONFIG_PATH)

API_KEY = CUSTOM_CONFIG.get("APIKEY", "")
LLM_API_KEY = CUSTOM_CONFIG.get("LLM_APIKEY", "")

# The project pattern uses a custom /responses endpoint for OpenRouter
RESPONSES_API_ENDPOINT = "https://openrouter.ai/api/v1/responses"

API_CONFIG = {
    "model": "openai/gpt-4o",
    "vision_model": "openai/gpt-4o",
    "max_output_tokens": 16384,
    "instructions": """Jesteś agentem transportowym Systemu Przesyłek Konduktorskich (SPK).

Twoim zadaniem jest przygotowanie poprawnej deklaracji transportu dla przesyłki z Gdańska do Żarnowca.

DANE WEJŚCIOWE:
- Nadawca: 450202122
- Punkt nadawczy: Gdańsk
- Punkt docelowy: Żarnowiec
- Waga: 2800 kg
- Budżet: 0 PP (musi być darmowa lub opłacana przez System)
- Zawartość: kasety z paliwem do reaktora
- Uwagi specjalne: brak

KROKI DO WYKONANIA:
1. Przeczytaj dokumentację (list_docs, read_doc). Zwróć uwagę na wzór deklaracji w zalacznik-E.md.
2. Przeanalizuj mapę/trasy (get_image_path, vision_analyze). Ustal kod trasy Gdańsk - Żarnowiec (powinien to być X-01).
3. Oblicz liczbę dodatkowych wagonów (WDP). 
   - Standardowy skład to lokomotywa + 2 wagony (udźwig 500kg każdy, razem 1000kg).
   - Każdy dodatkowy wagon (WDP) zwiększa udźwig o 500kg.
   - Dla 2800kg potrzebujesz łącznie 6 wagonów, czyli 4 DODATKOWE (WDP: 4).
4. Ustal kategorię przesyłki. Paliwo jądrowe to Kategoria A (Strategiczna).
5. Kategoria A jest zwolniona z opłat (OB=0, OW=0, OT=0) oraz z opłat za dodatkowe wagony (WDP są darmowe).
6. Wypełnij deklarację dokładnie wg wzoru (DATA: 2026-03-18, PUNKT NADAWCZY: Gdańsk, NADAWCA: 450202122, PUNKT DOCELOWY: Żarnowiec, TRASA: X-01, KATEGORIA: A, WDP: 4, KWOTA: 0 PP).
7. Prześlij deklarację do weryfikacji (submit_declaration).
"""
}

DOCS_DIR = Path(__file__).parent.parent / "docs"
