# api.py

import random
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import re

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
    # Ensure number is a valid integer
    try:
        num = int(request.number)
        if num <= 0:
            num = 1  # Default to 1 if negative or zero
    except (ValueError, TypeError):
        num = 1  # Default to 1 if not a valid number
        
    caption_type = (num - 1) % 3 + 1
    print(f"Number: {num}, Caption type: {caption_type}")
    
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
            "You are a creative assistant generating a single social media caption. "
            "EXTREMELY IMPORTANT: Generate only ONE caption, not multiple options. "
            "DO NOT number your response or provide alternatives. DO NOT write phrases like 'Caption:' or 'Here's your caption'. "
            "The entire response should be ONLY the caption text that would appear in a social media post. "
            "Keep the tone fresh, flirty, and inviting. Avoid hashtags and tags. "
            "If relevant, mention only one news or weather item—no extra topics."
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
            "You are a creative assistant generating a single social media caption. "
            "EXTREMELY IMPORTANT: Generate only ONE caption, not multiple options. "
            "DO NOT number your response or provide alternatives. DO NOT write phrases like 'Caption:' or 'Here's your caption'. "
            "The entire response should be ONLY the caption text that would appear in a social media post. "
            "Create a conversational, emotional reaction to the news headline. "
            "Add your personal opinion, with expressions like 'Can you believe...?', 'I can't even...', 'So much for...' "
            "Write as if you're texting a friend about the news with your raw emotional response. "
            "Use casual language, rhetorical questions, and authentic reactions. "
            "Keep it concise and avoid adding your own hashtags or tags."
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
            "You are a creative assistant generating a single social media caption. "
            "EXTREMELY IMPORTANT: Generate only ONE caption, not multiple options. "
            "DO NOT number your response or provide alternatives. DO NOT write phrases like 'Caption:' or 'Here's your caption'. "
            "The entire response should be ONLY the caption text that would appear in a social media post. "
            "Focus on a single local concert or festival event. Do not add unrelated topics. "
            "Keep it concise and avoid adding your own hashtags or tags."
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
        "n": 1,
        "max_tokens": 100,     # Limit output length
        "temperature": 0.7,    # Control randomness (lower = more deterministic)
        "top_p": 0.9           # Control diversity of responses
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
        
        # 2. Remove any "Caption:" or similar prefixes or meta-responses
        prefixes = [
            "Caption:", "Text:", "Post:", "Social media caption:", 
            "Here's your", "Here is your", "Here is a", "Here's a",
            "I've created", "I have created", "This caption", "Your caption"
        ]
        for prefix in prefixes:
            if generated_text.lower().startswith(prefix.lower()):
                # Find the first colon or period after the prefix
                colon_pos = generated_text.find(':', len(prefix))
                period_pos = generated_text.find('.', len(prefix))
                
                if colon_pos > 0:
                    generated_text = generated_text[colon_pos + 1:].strip()
                elif period_pos > 0:
                    generated_text = generated_text[period_pos + 1:].strip()
                else:
                    # If no colon/period found, just remove the prefix
                    generated_text = generated_text[len(prefix):].strip()
        
        # Additional check to remove common phrases that indicate meta-text
        meta_phrases = [
            "fresh", "flirty", "inviting", "caption", "social media", 
            "based on", "referencing", "incorporating", "weather"
        ]
        
        # Check if the first sentence is just meta-description
        first_sentence_end = generated_text.find('.')
        if first_sentence_end > 0:
            first_sentence = generated_text[:first_sentence_end].lower()
            has_meta = any(phrase in first_sentence for phrase in meta_phrases)
            
            # If the first sentence appears to be meta-text, remove it
            if has_meta and len(generated_text) > first_sentence_end + 1:
                generated_text = generated_text[first_sentence_end + 1:].strip()
        
        # 3. Ensure proper spacing and capitalization
        generated_text = generated_text.strip()
        if generated_text and not generated_text[0].isupper() and generated_text[0].isalpha():
            generated_text = generated_text[0].upper() + generated_text[1:]
        
        # 4. Fallback if generated text is empty or just punctuation
        # Check if the text is empty, too short, or just punctuation
        is_valid_text = (
            generated_text and 
            len(generated_text) > 5 and  # Ensure it's not just a few characters
            not re.match(r'^[^\w\s]*$', generated_text)  # Not just punctuation
        )
        
        if not is_valid_text:
            print(f"WARNING: DeepSeek API returned invalid caption: '{generated_text}', using fallback")
            # Use a direct caption from our templates based on caption type
            fallback_captions = {
                "baity": [
                    "Living my best life ✨",
                    "Ready for a spontaneous adventure",
                    "Friday mood: activated",
                    "Feeling a bit too good today",
                    "Making memories in " + location
                ],
                "opinion": [
                    "Been thinking about this lately",
                    "Some thoughts on a rainy day",
                    "Hot take: less is more",
                    "Quality over quantity, always",
                    "Sometimes the simple things matter most"
                ],
                "event": [
                    "Weekend plans loading...",
                    "Ready for the next adventure",
                    "Looking for recommendations in " + location,
                    "Who's up for exploring the local scene?",
                    "Counting down to the weekend"
                ]
            }
            
            # Get fallbacks for the current caption type or use baity as default
            available_fallbacks = fallback_captions.get(caption_type_str, fallback_captions["baity"])
            generated_text = random.choice(available_fallbacks)
        
        # Extract only the first caption if multiple are returned (for any caption type)
        if '\n\n' in generated_text:
            # Split by double newlines and take only the first caption
            first_caption = generated_text.split('\n\n')[0].strip()
            print(f"Multiple captions detected, using only the first one: '{first_caption}'")
            generated_text = first_caption
        
        # Final cleanup - normalize whitespace and remove any line breaks
        generated_text = re.sub(r'\s+', ' ', generated_text).strip()
        
        # Final length check
        if len(generated_text) > 280:  # Twitter-style length limit
            print(f"Caption too long ({len(generated_text)} chars), truncating")
            # Try to truncate at a sentence boundary
            last_period = generated_text[:280].rfind('.')
            if last_period > 180:  # If we can get a reasonably long caption
                generated_text = generated_text[:last_period+1]
            else:
                generated_text = generated_text[:280]
        
        # Add location hashtag with 50% chance for all caption types
        if random.random() < 0.5:  # 50% chance
            # Format location as hashtag - keep first letters of words capitalized for readability
            # Remove spaces, special chars and ensure first letters remain capitalized
            parts = location.split()
            if len(parts) > 1:
                # For multi-word locations (like "New York"), create a camel case hashtag (#NewYork)
                clean_location = ''.join(
                    part.capitalize() for part in parts if part
                )
            else:
                # For single-word locations, just capitalize and clean
                clean_location = location.capitalize()
            
            # Remove any remaining non-alphanumeric characters
            clean_location = ''.join(c for c in clean_location if c.isalnum())
            
            # Make sure we have a valid hashtag
            if clean_location:
                # Decide whether to add it on the same line or a new line
                if random.random() < 0.5:  # 50% chance for same line
                    generated_text = f"{generated_text} #{clean_location}"
                else:  # 50% chance for new line
                    generated_text = f"{generated_text}\n\n#{clean_location}"
                    
                print(f"Added location hashtag: #{clean_location}")
        
        return CaptionResponse(caption=generated_text, caption_type=caption_type_str)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek API Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 