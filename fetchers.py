import os
import requests
import feedparser
import random
from urllib.parse import quote_plus
from typing import Optional, Tuple

from config import URL_WEATHER, WEATHER_API_KEY

# --- Existing weather fetcher ---
def fetch_weather(location: str) -> Tuple[str, str, str]:
    url_call = f"{URL_WEATHER}?key={WEATHER_API_KEY}&q={location}&aqi=no"
    response = requests.get(url_call)
    if response.status_code == 200:
        data = response.json()
        city = data['location']['name']
        state = data['location']['region']
        condition = data['current']['condition']['text'].lower()
        weather_descriptions = {
            "sunny": "bright and sunny",
            "cloudy": "a bit cloudy",
            "partly cloudy": "a mix of sun and clouds",
            "rainy": "a little rainy",
            "stormy": "wild and stormy",
            "clear": "clear and beautiful",
            "snowy": "a winter wonderland"
        }
        weather_condition = weather_descriptions.get(condition, condition)
        return weather_condition, city, state
    else:
        print(f"Weather API Error {response.status_code}: {response.text}")
        return "Could not fetch weather data", None, None

# --- Existing news fetcher ---
def fetch_news_rss(city: str) -> str:
    city_encoded = quote_plus(city)
    feed_url = (
        f"https://news.google.com/rss/search?"
        f"q={city_encoded}+news&hl=en-US&gl=US&ceid=US:en"
    )
    feed = feedparser.parse(feed_url)
    if feed.entries:
        return feed.entries[0].title
    return f"No trending news in {city}."

# --- Geocoding helper using OpenStreetMap Nominatim ---
def geocode(location: str) -> Optional[Tuple[float, float]]:
    """
    Convert any location string into latitude and longitude via Nominatim.
    Returns (lat, lon) or None if not found.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json", "limit": 1}
    headers = {"User-Agent": "CaptionBot/1.0"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon
    except Exception:
        return None

# --- PredictHQ event fetcher with geocoding ---
PREDICTHQ_TOKEN = os.getenv("PREDICTHQ_TOKEN") or "YOUR_PREDICTHQ_TOKEN_HERE"

def fetch_predicthq_event(location: str, radius_km: int = 25) -> dict:
    """
    Fetch one upcoming event from PredictHQ around any location string.
    Returns dict with keys: valid, artist, venue, city, date, event.
    """
    coords = geocode(location)
    if not coords:
        return {"valid": False}

    lat, lon = coords
    url = "https://api.predicthq.com/v1/events/"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {PREDICTHQ_TOKEN}"
    }
    params = {
        "within": f"{radius_km}km@{lat},{lon}",
        "country": "US",
        "active": "true",
        "limit": 1
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=5)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if not results:
            return {"valid": False}

        ev = results[0]
        title   = ev.get("title", "")
        venue   = ev.get("venue", {}).get("label", "") or ""
        start   = ev.get("start", "")
        city_nm = location.split(",")[0]

        return {
            "valid": True,
            "artist": title,
            "venue": venue,
            "city": city_nm,
            "date": start,
            "event": title
        }
    except Exception:
        return {"valid": False}
