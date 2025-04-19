import os
import csv

# Major US cities list
US_CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte",
    "San Francisco", "Indianapolis", "Seattle", "Denver", "Washington"
]

def load_captions():
    """Load caption templates from CSV files"""
    captions_dir = os.path.join(os.path.dirname(__file__), 'data')
    baity_captions = []
    opinion_captions = []
    
    # Load baity captions
    baity_path = os.path.join(captions_dir, 'baity_captions.csv')
    if os.path.exists(baity_path):
        with open(baity_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            baity_captions = [row[0] for row in reader if row]
    
    # Load opinion captions
    opinion_path = os.path.join(captions_dir, 'opinion_captions.txt')
    if os.path.exists(opinion_path):
        with open(opinion_path, 'r', encoding='utf-8') as f:
            opinion_captions = [line.strip() for line in f if line.strip()]
    
    return baity_captions, opinion_captions
