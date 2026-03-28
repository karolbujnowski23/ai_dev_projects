import pandas as pd
import requests
from io import StringIO
from .helpers.logger import log

CITIES_URL = "https://hub.ag3nts.org/dane/s03e04_csv/cities.csv"
ITEMS_URL = "https://hub.ag3nts.org/dane/s03e04_csv/items.csv"
CONNECTIONS_URL = "https://hub.ag3nts.org/dane/s03e04_csv/connections.csv"

def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Loads cities, items, and connections data from CSVs into pandas DataFrames.
    """
    try:
        cities_response = requests.get(CITIES_URL)
        cities_response.raise_for_status()
        cities_df = pd.read_csv(StringIO(cities_response.text))
        log.success("Successfully loaded cities.csv")

        items_response = requests.get(ITEMS_URL)
        items_response.raise_for_status()
        items_df = pd.read_csv(StringIO(items_response.text))
        log.success("Successfully loaded items.csv")
        
        connections_response = requests.get(CONNECTIONS_URL)
        connections_response.raise_for_status()
        connections_df = pd.read_csv(StringIO(connections_response.text))
        log.success("Successfully loaded connections.csv")
        
        return cities_df, items_df, connections_df

    except requests.exceptions.RequestException as e:
        log.error(f"Error downloading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        log.error(f"Error processing data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def find_cities_with_all_items(item_list: list, items_df: pd.DataFrame, cities_df: pd.DataFrame, connections_df: pd.DataFrame) -> list:
    """
    Finds cities that have all the specified items.
    """
    if not item_list or items_df.empty or connections_df.empty or cities_df.empty:
        return []

    # Get all unique item names from the dataframe
    all_available_items = items_df['name'].str.lower().unique()

    # Find which of the requested items are available in our data
    found_items = [item for item in item_list if item in all_available_items]

    if not found_items:
        return []

    # Start with cities that have the first item
    first_item_code = items_df[items_df['name'].str.lower() == found_items[0]]['code'].values[0]
    cities_with_item = set(connections_df[connections_df['itemCode'] == first_item_code]['cityCode'])

    # Intersect with cities that have the other items
    for item in found_items[1:]:
        item_code = items_df[items_df['name'].str.lower() == item]['code'].values[0]
        cities_with_item.intersection_update(set(connections_df[connections_df['itemCode'] == item_code]['cityCode']))

    if not cities_with_item:
        return []

    # Get city names from city codes
    city_names = cities_df[cities_df['code'].isin(cities_with_item)]['name'].tolist()
    
    return city_names