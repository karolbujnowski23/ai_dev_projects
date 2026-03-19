import pandas as pd
import requests
import io
import logging

logger = logging.getLogger(__name__)

def fetch_latest_data(url: str) -> list[dict]:
    """Pobiera najświeższą wersję pliku CSV z podanego URL huba. Zwraca listę słowników z danymi (id, description)."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parsowanie pliku CSV do DataFrame, a następnie do listy słowników
        csv_data = io.StringIO(response.text)
        df = pd.read_csv(csv_data)
        
        # Oczekiwany format: np. columns ['id', 'description']
        items = df.to_dict(orient='records')
        logger.info(f"Pobrano pomyślnie {len(items)} elementów z huba.")
        return items
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Błąd podczas pobierania danych z CSV: {e}")
        raise
