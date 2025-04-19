# fetchers.py

import requests
import feedparser
from datetime import datetime
import random
from urllib.parse import quote_plus
from config import URL_WEATHER, WEATHER_API_KEY, TICKETMASTER_API_KEY

def fetch_weather(location: str) -> tuple[str, str, str]:
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

def fetch_news_rss(city: str) -> str:
    city_encoded = quote_plus(city)
    feed_url = f"https://news.google.com/rss/search?q={city_encoded}+news&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(feed_url)
    if feed.entries:
        headline = feed.entries[0].title
        return headline
    return f"No trending news in {city}."

def fetch_ticketmaster_event(city: str = None) -> dict:
    """
    Fetch a random major event from popular US cities or a specific city
    """
    # Build URL with API key in parameters
    base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
    # Major US cities with high event probability
    us_cities = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
        "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
        "Austin", "Jacksonville", "Fort Worth", "Columbus", "San Francisco"
    ]
    
    # If city is not provided, choose a random one
    if not city:
        city = random.choice(us_cities)
    
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "city": city,
        "countryCode": "US",
        "locale": "*",
        "size": "3",
        "sort": "date,asc"
    }
    
    # Debug prints to verify request details
    try:
        # Let requests handle URL parameter encoding
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        print(f"API Error: {str(e)}")
        return {"error": "Could not fetch events from Ticketmaster API", "valid": False}
    
    print("DEBUG: Response Code:", response.status_code)
    print("DEBUG: Response Body:", response.text)
    
    if response.status_code == 200:
        data = response.json()
        
        if not data.get('_embedded') or not data['_embedded'].get('events'):
            return {"error": "No events found in random city search", "valid": False}
        
        event = data['_embedded']['events'][0]
        venues = event.get('_embedded', {}).get('venues', [])
        
        # Validate at least one venue exists
        if not venues:
            return {"error": "No venue information available", "valid": False}
        
        # Extract venue details
        venue_info = event.get('_embedded', {}).get('venues', [{}])[0]
        venue_name = venue_info.get('name', 'a cool venue')
        city = venue_info.get('city', {}).get('name', 'the city')
        
        # Get first valid artist name or use event name
        attractions = event.get('_embedded', {}).get('attractions', [])
        artist = next((
            a['name'] for a in attractions 
            if a.get('name') and not a.get('name').startswith(('TBD', 'To Be Announced'))
        ), event.get('name', 'Local Performers'))
            
        event_name = event.get('name', 'Live Music')
        event_date = event.get('dates', {}).get('start', {}).get('localDate', 'soon')
            
            # Safely get artist name with fallbacks
        return {
            "artist": artist or "amazing performers",
            "venue": venue_name,
            "city": city,
            "date": event_date,
            "event": event_name,
            "valid": True  # Flag for successful event data
        }
        
    print(f"Ticketmaster API Error {response.status_code}: {response.text}")
    return {"error": "Could not fetch events from Ticketmaster API", "valid": False}
