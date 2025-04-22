#!/usr/bin/env python3
# test_opinions.py - Test script for opinion captions

import requests
import time
import random

def test_opinion_captions(locations=None):
    """Test generating opinion captions for multiple locations."""
    if locations is None:
        locations = [
            "New York", "Los Angeles", "Chicago", "Houston", "Miami",
            "San Francisco", "Boston", "Seattle", "Austin", "Nashville"
        ]
    
    url = "http://localhost:8000/generate"
    
    print("\n===== TESTING OPINION CAPTIONS =====\n")
    print(f"Testing {len(locations)} different locations...\n")
    
    for location in locations:
        # Opinion captions are generated with number=2 (or any n where (n-1)%3 = 1)
        data = {
            "location": location,
            "number": 2
        }
        
        print(f"\n----- Location: {location} -----")
        
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            print(f"Caption Type: {result['caption_type'].upper()}")
            print(f"Caption: {result['caption']}")
            
            # Add a small delay between requests to avoid overwhelming the server
            time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            print(f"Error: {str(e)}")
            
        print("-" * 50)

if __name__ == "__main__":
    # You can customize the list of locations here
    test_locations = [
        "New York", 
        "Los Angeles", 
        "Chicago",
        "Seattle",
        "New Jersey",
        "Miami",
        "Atlanta",
        "Nashville",
        "Portland",
        "Denver"
    ]
    
    # Shuffle the locations for more randomness
    random.shuffle(test_locations)
    
    # Test with random 5 locations
    test_opinion_captions(test_locations[:5]) 