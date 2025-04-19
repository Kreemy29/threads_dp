#!/usr/bin/env python3
# client_example.py

import requests
import sys

def get_caption(location, number):
    """Generate a caption using the API."""
    url = "http://localhost:8000/generate"
    data = {
        "location": location,
        "number": number
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        return f"Caption Type: {result['caption_type'].upper()}\nLocation: {location}\nCaption: {result['caption']}"
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Get location from command line or use default
    location = sys.argv[1] if len(sys.argv) > 1 else "New York"
    
    # Generate captions with different numbers
    for i in range(1, 4):
        print(f"\n--- Caption {i} ---")
        caption = get_caption(location, i)
        print(caption)
        print("-" * 50) 