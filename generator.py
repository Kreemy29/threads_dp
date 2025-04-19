# generator.py

import random
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
    1. Weather-related (20% chance)
    2. News-related (20% chance)
    3. A generic baity caption without location specifics (60% chance)
    
    Note: This function should return exactly ONE caption.
    """
    # Get reference captions from data file
    from data import load_captions
    reference_captions, _ = load_captions()
    
    # Decide which type of caption to generate
    caption_type = random.choices(
        ["weather", "news", "generic"], 
        weights=[20, 20, 60],
        k=1
    )[0]
    
    if caption_type == "weather":
        # Weather-related caption
        try:
            weather_condition, city_name, state_name = fetch_weather(location)
            if city_name and state_name:
                return random.choice(weather_caption_templates).format(
                    weather_condition=weather_condition,
                    city_name=city_name
                )
        except Exception:
            # Fall back to generic if weather fetch fails
            caption_type = "generic"
    
    if caption_type == "news":
        # News-related caption
        try:
            news_summary = fetch_news_rss(location)
            return random.choice(news_caption_templates).format(news_summary=news_summary)
        except Exception:
            # Fall back to generic if news fetch fails
            caption_type = "generic"
    
    # Generic caption (no location specifics)
    # Filter out only captions that don't contain placeholders
    generic_captions = [
        cap for cap in reference_captions 
        if "{" not in cap and "}" not in cap
    ]
    
    if generic_captions:
        return random.choice(generic_captions)
    else:
        # Fallback if no suitable generic captions found
        return "Living my best life ✨"

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
