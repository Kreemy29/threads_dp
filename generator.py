# generator.py

import random
import os
from templates import (
    weather_caption_templates, 
    news_caption_templates, 
    opinion_caption_templates, 
    event_caption_templates,
    fallback_event_captions
)
from fetchers import fetch_weather, fetch_news_rss, fetch_ticketmaster_event

def generate_baity_prompt(location: str) -> str:
    """
    Generate a single baity caption that is either:
    1. Weather-related (15% chance)
    2. News-related (15% chance)
    3. Location-based caption (30% chance)
    4. A generic baity caption without location specifics (40% chance)
    
    Note: This function should return exactly ONE caption.
    """
    # Get reference captions from data file
    from data import load_captions
    reference_captions, _ = load_captions()
    
    # Always have a fallback caption ready
    fallback_captions = [
        "Living my best life ✨",
        "Ready for whatever comes next",
        "Some days just hit different",
        "The vibe today is immaculate",
        "Too busy being awesome",
        "Just here making memories"
    ]
    
    # Make sure we have some captions to work with
    if not reference_captions:
        print("Warning: No reference captions found, using fallbacks")
        return random.choice(fallback_captions)
    
    # Load location-specific captions if the file exists
    location_captions = []
    location_path = os.path.join(os.path.dirname(__file__), 'data', 'location_captions.txt')
    if os.path.exists(location_path):
        with open(location_path, 'r', encoding='utf-8') as f:
            location_captions = [line.strip() for line in f if line.strip()]
    
    # Decide which type of caption to generate
    caption_type = random.choices(
        ["weather", "news", "location", "generic"], 
        weights=[15, 15, 30, 40],
        k=1
    )[0]
    
    # Weather caption - only try if city_name is not None
    if caption_type == "weather":
        try:
            weather_condition, city_name, state_name = fetch_weather(location)
            if city_name and state_name and weather_condition:
                weather_caption = random.choice(weather_caption_templates).format(
                    weather_condition=weather_condition,
                    city_name=city_name
                )
                print(f"Generated weather caption: {weather_caption}")
                return weather_caption
            else:
                print("Weather caption generation failed: Missing city or weather data")
        except Exception as e:
            print(f"Weather caption error: {str(e)}")
        # Fall back to reference caption if weather fails
        caption_type = "reference"
    
    # News caption - only try if news_summary is not None
    if caption_type == "news":
        try:
            news_summary = fetch_news_rss(location)
            if news_summary:
                news_caption = random.choice(news_caption_templates).format(news_summary=news_summary)
                print(f"Generated news caption: {news_caption}")
                return news_caption
            else:
                print("News caption generation failed: No news summary")
        except Exception as e:
            print(f"News caption error: {str(e)}")
        # Fall back to reference caption if news fails
        caption_type = "reference"
            
    # Location caption - only try if we have location captions
    if caption_type == "location" and location_captions:
        try:
            location_caption = random.choice(location_captions)
            # Replace {city_name} placeholder if present
            if "{city_name}" in location_caption:
                location_caption = location_caption.replace("{city_name}", location)
            print(f"Generated location caption: {location_caption}")
            return location_caption
        except Exception as e:
            print(f"Location caption error: {str(e)}")
        # Fall back to reference caption if location fails
        caption_type = "reference"
    
    # Try generic caption (without placeholders)
    if caption_type == "generic":
        generic_captions = [
            cap for cap in reference_captions 
            if "{" not in cap and "}" not in cap
        ]
        
        if generic_captions:
            generic_caption = random.choice(generic_captions)
            print(f"Generated generic caption: {generic_caption}")
            return generic_caption
    
    # Always fall back to selecting any reference caption if all else fails
    # This ensures we always return something
    if reference_captions:
        random_caption = random.choice(reference_captions)
        # Clean any placeholders from the caption
        if "{" in random_caption and "}" in random_caption:
            # Simple substitution for common placeholders
            random_caption = random_caption.replace("{city_name}", location)
            random_caption = random_caption.replace("{weather_condition}", "amazing")
            random_caption = random_caption.replace("{news_summary}", "the latest happenings")
        print(f"Falling back to random reference caption: {random_caption}")
        return random_caption
    
    # Ultimate fallback if everything else fails
    print("All generation methods failed, using ultimate fallback")
    return random.choice(fallback_captions)

def generate_opinion_prompt(base_prompt: str, location: str) -> str:
    """Merges user-provided base prompt with a single local news reference."""
    news_summary = fetch_news_rss(location)
    template = random.choice(opinion_caption_templates)
    return template.format(base_prompt=base_prompt, news_summary=news_summary)

def generate_event_prompt(base_prompt: str) -> str:
    """Generate event caption with max 5s total timeout"""
    from data import US_CITIES
    import time
    
    start_time = time.time()
    timeout = 5  # seconds
    cities_tried = []
    
    while time.time() - start_time < timeout:
        city = random.choice(US_CITIES)
        if city in cities_tried:
            continue
            
        cities_tried.append(city)
        time.sleep(0.5)  # Add delay between attempts
        try:
            print(f"====== Trying to fetch event for city: {city} ======")
            event_summary = fetch_ticketmaster_event(city)
            print(f"Event valid: {event_summary.get('valid', False)}")
            print(f"Event artist: {event_summary.get('artist', 'None')}")
            print(f"Event venue: {event_summary.get('venue', 'None')}")
            
            if isinstance(event_summary, dict) and event_summary.get('valid') and isinstance(event_summary.get('artist'), str):
                template = random.choice(event_caption_templates)
                print(f"Selected template: {template}")
                
                formatted_caption = template.format(
                    base_prompt=base_prompt,
                    artist=event_summary.get('artist', 'amazing performers'),
                    venue=event_summary.get('venue', 'a cool venue'),
                    city=event_summary.get('city', 'the city'),
                    date=event_summary.get('date', 'soon'),
                    event=event_summary.get('event', 'Live Music')
                )
                
                print(f"SUCCESS! Formatted caption: {formatted_caption}")
                return formatted_caption
        except Exception as e:
            print(f"Event generation error for {city}: {str(e)}")
            
        # Check timeout after each attempt
        if time.time() - start_time >= timeout:
            break
    
    print(f"Timeout after {len(cities_tried)} attempts in {time.time()-start_time:.1f}s")
    return random.choice(fallback_event_captions).format(base_prompt=base_prompt)

def generate_event_prompt_with_location(base_prompt: str, location: str) -> str:
    """Generate event caption using the specified location with fallback to random cities"""
    import time
    from data import US_CITIES
    
    # First, try with the provided location
    try:
        print(f"====== Trying to fetch event for specified location: {location} ======")
        event_summary = fetch_ticketmaster_event(location)
        print(f"Event valid: {event_summary.get('valid', False)}")
        print(f"Event artist: {event_summary.get('artist', 'None')}")
        print(f"Event venue: {event_summary.get('venue', 'None')}")
        
        if isinstance(event_summary, dict) and event_summary.get('valid') and isinstance(event_summary.get('artist'), str):
            template = random.choice(event_caption_templates)
            print(f"Selected template: {template}")
            
            formatted_caption = template.format(
                base_prompt=base_prompt,
                artist=event_summary.get('artist', 'amazing performers'),
                venue=event_summary.get('venue', 'a cool venue'),
                city=event_summary.get('city', 'the city'),
                date=event_summary.get('date', 'soon'),
                event=event_summary.get('event', 'Live Music')
            )
            
            print(f"SUCCESS! Formatted caption with user location: {formatted_caption}")
            return formatted_caption
    except Exception as e:
        print(f"Event generation error for specified location {location}: {str(e)}")
    
    # If the specified location doesn't work, fall back to the original random approach
    print(f"Could not find events for {location}, falling back to random cities...")
    return generate_event_prompt(base_prompt)
