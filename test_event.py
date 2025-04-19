# test_event.py

import random
from generator import generate_event_prompt
from data import US_CITIES

def test_event_generation():
    """Test event generation specifically"""
    print("TESTING EVENT GENERATION")
    print("-" * 50)
    
    for _ in range(5):
        base_prompt = f"Test base prompt {random.randint(1, 100)}"
        print(f"\nTesting with base prompt: '{base_prompt}'")
        
        caption = generate_event_prompt(base_prompt)
        print(f"\nFINAL CAPTION: {caption}")
        print("-" * 50)

if __name__ == "__main__":
    test_event_generation() 