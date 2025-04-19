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
            # Skip header row if it exists
            header_skipped = False
            for row in reader:
                if not header_skipped:
                    # Check if this is the header row (typically contains "Caption")
                    if row and row[0].lower() == "caption":
                        header_skipped = True
                        continue
                    else:
                        header_skipped = True  # No header, but mark as skipped
                
                # Only add non-empty rows
                if row and row[0].strip():
                    baity_captions.append(row[0].strip())
    
    # Load opinion captions
    opinion_path = os.path.join(captions_dir, 'opinion_captions.txt')
    if os.path.exists(opinion_path):
        with open(opinion_path, 'r', encoding='utf-8') as f:
            opinion_captions = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(baity_captions)} baity captions and {len(opinion_captions)} opinion captions")
    return baity_captions, opinion_captions
