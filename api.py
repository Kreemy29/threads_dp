# api.py

import random
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from config import URL_DEEPSEEK, HEADERS
from data import load_captions
from generator import (
    generate_baity_prompt, 
    generate_opinion_prompt, 
    generate_event_prompt, 
    generate_event_prompt_with_location
)

app = FastAPI(title="Caption Generator API")

# Load caption templates on startup
captions_baity, captions_opinion = load_captions()
if not captions_baity or not captions_opinion:
    print("⚠️ Warning: Could not load captions. Check your CSV/TXT files.")
    captions_baity = ["Default baity caption placeholder"]
    captions_opinion = ["Default opinion caption placeholder"]

# Global sets to track used captions
used_baity = set()
used_opinion = set()
used_events = set()

class CaptionRequest(BaseModel):
    location: str
    number: int

class CaptionResponse(BaseModel):
    caption: str
    caption_type: str

@app.get("/")
def root():
    return {"message": "Caption Generator API is running. Use /generate endpoint to create captions."}

@app.post("/generate", response_model=CaptionResponse)
def generate_caption(request: CaptionRequest):
    """
    Generate a single caption based on location and number.
    - Numbers 1, 4, 7, 10... generate baity captions
    - Numbers 2, 5, 8... generate opinion captions
    - Numbers 3, 6, 9... generate event captions
    """
    # Validate location
    location = request.location.strip()
    if not location:
        raise HTTPException(status_code=400, detail="Location cannot be empty")
    
    # Determine caption type based on number (1-3 pattern repeating)
    caption_type = (request.number - 1) % 3 + 1
    
    if caption_type == 1:
        # Baity caption
        base_prompt = random.choice(captions_baity)
        # Avoid repetition
        if len(used_baity) >= len(captions_baity) * 0.8:  # Reset if 80% used
            used_baity.clear()
        while base_prompt in used_baity and len(used_baity) < len(captions_baity):
            base_prompt = random.choice(captions_baity)
        used_baity.add(base_prompt)
        
        dynamic_prompt = generate_baity_prompt(location)
        system_content = (
            "You are a creative assistant generating a single, fresh, flirty, and inviting social media caption. "
            "Keep the tone cheeky and engaging, but avoid using hashtags or tags. "
            "Generate exactly ONE caption, not a list of options. "
            "Mention only one news or weather item if relevant—do not add extra topics."
        )
        user_message = f"{base_prompt}\n\n{dynamic_prompt}"
        caption_type_str = "baity"
        
    elif caption_type == 2:
        # Opinion caption
        base_prompt = random.choice(captions_opinion)
        # Avoid repetition
        if len(used_opinion) >= len(captions_opinion) * 0.8:  # Reset if 80% used
            used_opinion.clear()
        while base_prompt in used_opinion and len(used_opinion) < len(captions_opinion):
            base_prompt = random.choice(captions_opinion)
        used_opinion.add(base_prompt)
        
        dynamic_prompt = generate_opinion_prompt(base_prompt, location)
        system_content = (
            "You are a creative assistant generating real, relatable, and location-based social media captions. "
            "Reference only the single local news headline. Do not add extra or unrelated topics. "
            "Keep it concise and avoid hashtags or tags."
        )
        user_message = dynamic_prompt
        caption_type_str = "opinion"
        
    else:  # caption_type == 3
        # Event caption
        base_prompt = random.choice(captions_opinion)  # Reusing opinion captions as base
        # Avoid repetition
        if len(used_events) >= len(captions_opinion) * 0.8:  # Reset if 80% used
            used_events.clear()
        while base_prompt in used_events and len(used_events) < len(captions_opinion):
            base_prompt = random.choice(captions_opinion)
        used_events.add(base_prompt)
        
        # Use the location-aware event prompt generator
        # This will try the user's location first, then fall back to random cities if needed
        dynamic_prompt = generate_event_prompt_with_location(base_prompt, location)
        
        system_content = (
            "You are a creative assistant generating real, relatable, and location-based social media captions "
            "focusing on a single local concert or festival event. Do not add unrelated topics. "
            "Keep it concise and avoid hashtags or tags."
        )
        user_message = dynamic_prompt
        caption_type_str = "event"
    
    # Call DeepSeek API to generate the final caption
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message}
        ],
        "stream": False,
        "n": 1
    }
    
    try:
        response = requests.post(URL_DEEPSEEK, json=payload, headers=HEADERS)
        response.raise_for_status()
        generated_text = response.json().get("choices", [])[0]['message']['content']
        
        # For baity captions, extract only the first caption if multiple are returned
        if caption_type_str == 'baity' and '\n\n' in generated_text:
            # Split by double newlines and take only the first caption
            generated_text = generated_text.split('\n\n')[0].strip()
        
        # Check for and replace any remaining placeholders in the text
        if '{city_name}' in generated_text and caption_type_str == 'baity':  # For baity captions
            # Replace with location or a reasonable default
            generated_text = generated_text.replace('{city_name}', location)
            
        if '{weather_condition}' in generated_text and caption_type_str == 'baity':
            # Replace with a default weather condition
            generated_text = generated_text.replace('{weather_condition}', 'lovely')
            
        if '{news_summary}' in generated_text:
            # Replace with a generic news reference
            generated_text = generated_text.replace('{news_summary}', f'the latest happenings in {location}')
            
        # For event captions, replace any remaining placeholders
        for placeholder in ['{artist}', '{venue}', '{city}', '{date}', '{event}']:
            if placeholder in generated_text:
                # Use reasonable defaults
                defaults = {
                    '{artist}': 'amazing performers',
                    '{venue}': 'a great venue',
                    '{city}': location,
                    '{date}': 'soon',
                    '{event}': 'exciting event'
                }
                generated_text = generated_text.replace(placeholder, defaults.get(placeholder, 'wonderful'))
        
        # Clean up the caption:
        # 1. Remove any quotes (single, double, smart quotes)
        for quote in ['"', "'", """, """, "'", "'"]:
            generated_text = generated_text.replace(quote, '')
        
        # 2. Remove any "Caption:" or similar prefixes
        prefixes = ["Caption:", "Text:", "Post:", "Social media caption:"]
        for prefix in prefixes:
            if generated_text.startswith(prefix):
                generated_text = generated_text[len(prefix):].strip()
        
        # 3. Ensure proper spacing and capitalization
        generated_text = generated_text.strip()
        if generated_text and not generated_text[0].isupper() and generated_text[0].isalpha():
            generated_text = generated_text[0].upper() + generated_text[1:]
        
        return CaptionResponse(caption=generated_text, caption_type=caption_type_str)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek API Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 