# config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys - read exclusively from environment variables
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
TICKETMASTER_API_KEY = os.environ.get("TICKETMASTER_API_KEY")

# Add validation to ensure keys are set
if not all([DEEPSEEK_API_KEY, WEATHER_API_KEY, TICKETMASTER_API_KEY]):
    missing_keys = []
    if not DEEPSEEK_API_KEY: missing_keys.append("DEEPSEEK_API_KEY")
    if not WEATHER_API_KEY: missing_keys.append("WEATHER_API_KEY")
    if not TICKETMASTER_API_KEY: missing_keys.append("TICKETMASTER_API_KEY")
    print(f"WARNING: Missing API keys in .env file: {', '.join(missing_keys)}")
    print("Please set these keys in your .env file.")

# URLs
URL_DEEPSEEK = "https://api.deepseek.com/chat/completions"
URL_WEATHER = "http://api.weatherapi.com/v1/current.json"
# (No need for Ticketmaster base URL here; we build it in code)

# Headers for DeepSeek
HEADERS = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}

# Get the base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# File paths - updated for containerized environment
DATA_DIR = Path(os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data")))

# Make sure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# File paths for caption data
BAITY_CSV_PATH = os.path.join(DATA_DIR, "baity_captions.csv")
OPINION_TXT_PATH = os.path.join(DATA_DIR, "opinion_captions.txt")
OUTPUT_FILE_PATH = os.path.join(DATA_DIR, "mixed_style_captions.txt")
