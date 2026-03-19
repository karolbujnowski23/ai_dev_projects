# -*- coding: utf-8 -*-

import os
from pathlib import Path

# Try to find .config in current dir, parent, or 2 levels up
def find_config():
    paths = [
        Path(".config"),
        Path("..") / ".config",
        Path("../..") / ".config",
        Path("../../../.config"),
        Path("../../../../.config"),
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

API_CONFIG = {
    "model": "openai/gpt-5-nano",
    "max_output_tokens": 4096,
    "instructions": """Jesteś operatorem systemu sterowania ruchem kolejowym. Twoim zadaniem jest AKTYWACJA trasy kolejowej o nazwie X-01.

DANE ZADANIA:
- Task: railway
- Trasa: X-01
- Akcja docelowa: Ustawienie statusu trasy X-01 na OTWARTY (RTOPEN).

KROKI DO WYKONANIA:
1. Uruchom 'get_help', aby dowiedzieć się jakie akcje są dostępne i w jakiej kolejności należy je wywoływać.
2. Na podstawie pomocy, przeprowadź proces modyfikacji statusu trasy:
   - Zazwyczaj wymaga to: 
     a) Przejścia w tryb rekonfiguracji (reconfigure) dla trasy X-01.
     b) Ustawienia statusu (setstatus) na RTOPEN.
     c) Zapisania zmian (save).
3. Kontynuuj, aż w odpowiedzi od serwera otrzymasz DWA różne flagi w formacie {FLG:...}. Nie przerywaj po znalezieniu pierwszej flagi – szukaj kolejnej.

WAŻNE: 
- API serwera kolejowego może zwracać błędy 503 (przeciążenie) lub limity zapytań. System MCP, z którego korzystasz, automatycznie zajmuje się retry i opóźnieniami.
- Jeśli jednak czas oczekiwania (retry_after + penalty) przekroczy 4 minuty, system zwróci błąd 'WAIT_TIME_EXCEEDED' i przerwie działanie.
- Nie zgaduj parametrów, używaj tylko tych z 'help'.

UWAGI:
- System jest celowo przeciążony, co wymaga cierpliwości.
- Czytaj błędy uważnie – jeśli akcja się nie powiedzie, komunikat błędu precyzyjnie wskazuje przyczynę (np. zły parametr lub kolejność).
- Twoim celem końcowym jest zebranie DWÓCH flag.
- Polegaj wyłącznie na dokumentacji zwróconej przez 'get_help'.
"""
}
