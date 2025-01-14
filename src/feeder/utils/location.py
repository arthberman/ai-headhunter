import json
import os
from pathlib import Path

import requests

URL = "https://linkedin-api8.p.rapidapi.com/search-locations"
DB_FILE = "db_geoAPI.json"


def load_cache():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_to_cache(keyword, data):
    cache = load_cache()
    cache[keyword] = data
    with open(DB_FILE, "w") as f:
        json.dump(cache, f, indent=4)


def read_location_cache(location: str) -> dict:
    cache_path = Path(__file__).parent / "db_geoAPI.json"
    try:
        with open(cache_path, "r") as f:
            cache = json.load(f)
            return cache.get(location, None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def add_location_to_cache(location: str, data: dict):
    """Add a new location to the cache file."""
    cache_path = Path(__file__).parent / "db_geoAPI.json"
    try:
        # Read existing cache
        with open(cache_path, "r") as f:
            cache = json.load(f)

        # Add new location
        cache[location] = data

        # Write updated cache
        with open(cache_path, "w") as f:
            json.dump(cache, f, indent=4)
        return True
    except Exception as e:
        print(f"Error adding location to cache: {e}")
        return False


def find_location(keyword):
    cache_path = Path(__file__).parent / "db_geoAPI.json"
    # Check cache first
    cached_response = read_location_cache(keyword)
    if cached_response:
        print("Using cached data...")
        return cached_response

    # If not in cache, make API call
    print("Making API call...")
    headers = {
        "x-rapidapi-key": "443a3625damshbed4425ab667ebep1b644ajsndcdbc2ce179b",
        "x-rapidapi-host": "linkedin-api8.p.rapidapi.com",
    }

    response = requests.get(URL, headers=headers, params={"keyword": keyword})
    data = response.json()

    # Save to cache using the new function
    add_location_to_cache(keyword, data)
    return data
