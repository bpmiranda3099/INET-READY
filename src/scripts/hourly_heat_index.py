from loguru import logger
import os
import csv
import requests
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from functions.calculate_heat_index import calculate_heat_index  # Import the function
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, '..', '..', 'public', 'data', 'city_coords.csv')

@lru_cache
def fetch_weather(latitude, longitude):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relative_humidity_2m"
    resp = requests.get(url).json()
    if "hourly" not in resp:
        logger.error(f"API response missing 'hourly' for lat={latitude}, lon={longitude}: {resp}")
        raise KeyError("hourly")
    celsius = resp["hourly"]["temperature_2m"][0]
    humidity = resp["hourly"]["relative_humidity_2m"][0]
    return celsius, humidity  # Return temperature in Celsius

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

    with ThreadPoolExecutor() as executor:
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
