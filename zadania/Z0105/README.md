# Railway Control Agent (Z0105)

Projekt automatycznego agenta operującego na systemie sterowania ruchem kolejowym. Zadaniem agenta jest aktywacja trasy **X-01** (zmiana statusu na `RTOPEN`) poprzez API, które jest celowo przeciążone i posiada bardzo restrykcyjne limity zapytań.

## Architektura

Projekt został zbudowany w oparciu o architekturę agentyczną z wykorzystaniem koncepcji **MCP (Model Context Protocol)**, co pozwala na oddzielenie logiki decyzyjnej modelu od technicznej warstwy komunikacji z API.

### Komponenty:
- **`src/agent.py`**: Główna pętla decyzyjna modelu. Agent analizuje stan systemu i decyduje o kolejnych krokach na podstawie dostępnych narzędzi.
- **`src/mcp/server.py`**: Warstwa wykonawcza (MCP Server). Zawiera logikę odporności (Resilience):
    - Obsługa błędów **503 (Service Unavailable)**.
    - Inteligentne zarządzanie limitami **429 (Rate Limit)** poprzez parsowanie pól `retry_after` oraz `penalty_seconds`.
    - Wymuszone przerwy techniczne (cool-off) dla zapewnienia stabilności połączenia.
- **`src/config.py`**: Konfiguracja agenta, prompt systemowy oraz automatyczne wyszukiwanie kluczy API.
- **`src/api.py`**: Integracja z OpenRouter (używany model: **GPT-5 Nano**).
- **`src/helpers/logger.py`**: Customowy system logowania zdarzeń (ramki, statusy, błędy).

## Narzędzia Agenta (Tools)
Agent posiada dostęp do następujących akcji:
- `get_help`: Pobiera dynamiczną dokumentację API (samo-dokumentujące się API).
- `reconfigure`: Aktywuje tryb edycji dla konkretnej trasy.
- `set_status`: Zmienia status trasy (np. na `RTOPEN`).
- `save`: Zapisuje wprowadzone zmiany.
- `get_status`: Sprawdza aktualny stan trasy.

## Wymagania i Uruchomienie

### Wymagania:
- Python 3.x
- Biblioteki: `httpx`, `requests`, `python-dotenv`
- Plik `.config` z kluczami `APIKEY` (AI_devs) oraz `LLM_APIKEY` (OpenRouter).

### Instalacja:
```powershell
pip install httpx requests python-dotenv
```

### Uruchomienie:
```powershell
python app.py
```

## Specyfika zadania
API zadania symuluje trudne warunki produkcyjne. Agent został zaprogramowany tak, aby cierpliwie czekać na reset limitów (nawet do 4 minut w przypadku blokad), co gwarantuje pomyślne ukończenie zadania bez ryzyka otrzymania permanentnej blokady (ban).
