"""
tools.py — Reusable tool functions for zadanie2.
Each function is independently callable and is also registered
as an LLM function-calling tool in agent.py.
"""

import math
import requests
from geopy.geocoders import Nominatim

def geocode_city(city_name: str, country: str = "Poland") -> dict:
    """
    Estimate GPS coordinates for a city name using Nominatim (OpenStreetMap).
    Returns {"lat": float, "lon": float} or raises ValueError if not found.
    """
    geolocator = Nominatim(user_agent="zadanie2_agent")
    location = geolocator.geocode(f"{city_name}, {country}")
    if location is None:
        raise ValueError(f"Could not geocode city: {city_name}")
    return {"lat": location.latitude, "lon": location.longitude}

def get_power_plant_locations(hub_base: str, hub_apikey: str) -> list[dict]:
    url = f"{hub_base}/data/{hub_apikey}/findhim_locations.json"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    raw = resp.json()  # e.g. {"Zabrze": {"is_active": True, "power": "35 MW", "code": "PWR3847PL"}, ...}
    # unwrap outer key if present
    if "power_plants" in raw:
        raw = raw["power_plants"]
    plants = []
    for city_name, info in raw.items():
        coords = geocode_city(city_name)          # <-- new call
        plants.append({
            "city":      city_name,
            "code":      info["code"],
            "is_active": info.get("is_active"),
            "power":     info.get("power"),
            "lat":       coords["lat"],
            "lon":       coords["lon"],
        })
    return plants


def get_person_locations(hub_base: str, hub_apikey: str, name: str, surname: str) -> list[dict]:
    """
    Fetch GPS coordinates where a person was spotted.

    Returns a list of dicts, each expected to contain at least:
        { "lat": float, "lon": float }
    """
    payload = {"apikey": hub_apikey, "name": name, "surname": surname}
    resp = requests.post(f"{hub_base}/api/location", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_access_level(hub_base: str, hub_apikey: str, name: str, surname: str, birth_year: int) -> int | dict:
    """
    Fetch the security access level for a person.

    Returns the parsed JSON — typically an integer or a dict with an 'accessLevel' key.
    """
    payload = {
        "apikey": hub_apikey,
        "name": name,
        "surname": surname,
        "birthYear": int(birth_year),
    }
    resp = requests.post(f"{hub_base}/api/accesslevel", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in kilometres using the Haversine formula."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi   = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_closest_plant(person_locations: list[dict], plants: list[dict]) -> dict | None:
    """
    Find which plant is geographically closest to any of a person's known locations.

    Args:
        person_locations: list of {"lat": ..., "lon": ...} dicts
        plants:           list of plant dicts (must include "lat", "lon", "code")

    Returns:
        {
            "plant":       <plant dict>,
            "distance_km": <float>,
            "location":    <person location dict>,
        }
        or None if either input list is empty.
    """
    best: dict | None = None
    for loc in person_locations:
        for plant in plants:
            dist = haversine_km(
                float(loc["lat"]),  float(loc["lon"]),
                float(plant["lat"]), float(plant["lon"]),
            )
            if best is None or dist < best["distance_km"]:
                best = {"plant": plant, "distance_km": dist, "location": loc}
    return best


def submit_answer(
    hub_base: str,
    hub_apikey: str,
    name: str,
    surname: str,
    access_level: int,
    power_plant_code: str,
) -> dict:
    """
    Submit the final answer to /verify.

    Returns the hub's JSON response (should contain a flag on success).
    """
    payload = {
        "apikey": hub_apikey,
        "task": "findhim",
        "answer": {
            "name": name,
            "surname": surname,
            "accessLevel": int(access_level),
            "powerPlant": power_plant_code,
        },
    }
    resp = requests.post(f"{hub_base}/verify", json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()
