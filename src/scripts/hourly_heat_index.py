from loguru import logger
import os
import csv
import requests

from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from functions.calculate_heat_index import calculate_heat_index  # Import the function
from datetime import datetime
import time
from dotenv import load_dotenv


script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, '..', '..', 'public', 'data', 'city_coords.csv')

# Load environment variables from .env
load_dotenv(os.path.join(script_dir, '..', '..', '.env'))
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
if not OPENWEATHERMAP_API_KEY:
    raise RuntimeError('OPENWEATHERMAP_API_KEY not set in .env')

@lru_cache
def fetch_weather(latitude, longitude):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}"
        f"&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error(f"OpenWeatherMap API error for lat={latitude}, lon={longitude}: {e}")
        time.sleep(1)
        raise

    if "main" not in data or "temp" not in data["main"] or "humidity" not in data["main"]:
        logger.error(f"API response missing 'main.temp' or 'main.humidity' for lat={latitude}, lon={longitude}: {data}")
        time.sleep(1)
        raise KeyError("main.temp or main.humidity")

    celsius = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    return celsius, humidity

def inet_level(heat_index):
    if heat_index < 27:
        return "low"
    elif 27 <= heat_index < 32:
        return "moderate"
    elif 32 <= heat_index < 41:
        return "high"
    else:
        return "very high"

def process_city(city):
    lat = float(city["Latitude"])
    lon = float(city["Longitude"])
    temp_c, humidity = fetch_weather(lat, lon)
    heat_index = calculate_heat_index(temp_c, humidity)  # Use the imported function
    now = datetime.now()
    return {
        "city": city["City"],
        "temperature": temp_c,
        "humidity": humidity,
        "heat_index": heat_index,
        "inet_level": inet_level(heat_index),
        "date_added": now.strftime("%Y-%m-%d"),
        "time_added": now.strftime("%H:%M:%S")
    }

def main():
    cities = []
    results = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cities.append(row)

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(process_city, c): c for c in cities}
        for future in as_completed(futures):
            city = futures[future]
            try:
                result = future.result()
                results.append(result)
                logger.info(result)
            except Exception as e:
                logger.error(f"Error processing {city['City']}: {e}")
    
    return results

if __name__ == "__main__":
    main()
