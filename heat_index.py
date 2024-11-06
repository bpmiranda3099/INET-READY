import csv
import requests
from requests.adapters import HTTPAdapter
import ssl
from dotenv import load_dotenv
import os
import time
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

# Determine the root directory of the script
root_dir = os.path.dirname(os.path.abspath(__file__))

# Configure logging to append to log.txt in the root directory
log_file = os.path.join(root_dir, 'log.txt')
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

# Load environment variables from a .env file
def configure():
    load_dotenv()

# Custom HTTPAdapter to lower SSL security level
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        kwargs['ssl_context'] = context
        return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)

# Calculate the heat index given temperature in Celsius and humidity
def calculate_heat_index(temperature_c, humidity):
    temperature_f = (temperature_c * 9/5) + 32
    heat_index_f = (-42.379 + 2.04901523 * temperature_f + 10.14333127 * humidity 
                    - 0.22475541 * temperature_f * humidity - 0.00683783 * temperature_f**2 
                    - 0.05481717 * humidity**2 + 0.00122874 * temperature_f**2 * humidity 
                    + 0.00085282 * temperature_f * humidity**2 - 0.00000199 * temperature_f**2 * humidity**2)
    heat_index_c = (heat_index_f - 32) * 5/9
    return heat_index_c

# Fetch weather data from the APIs with retry logic
@lru_cache(maxsize=128)
def get_weather(lat, lon, api_urls_tuple, retries=3, delay=5):
    for api_url in api_urls_tuple:
        success = False
        for attempt in range(retries):
            try:
                response = requests.get(api_url.format(lat=lat, lon=lon))
                response.raise_for_status()
                data = response.json()
                if 'main' in data:
                    temperature = data['main']['temp']
                    humidity = data['main']['humidity']
                elif 'current' in data:
                    temperature = data['current']['temp_c']
                    humidity = data['current']['humidity']
                elif 'hourly' in data:
                    temperature = data['hourly']['temperature_2m'][0]
                    humidity = data['hourly']['relative_humidity_2m'][0]
                else:
                    continue
                success = True
                return temperature, humidity
            except requests.exceptions.RequestException as e:
                sanitized_message = str(e).replace(api_url, "[REDACTED URL]")
                logging.error(f"Exception occurred while fetching data from API: {sanitized_message}")
                if attempt < retries - 1:
                    logging.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logging.error("Max retries reached. Moving to the next API.")
        if success:
            break
    return None, None

# Build an index of city coordinates from a CSV file
def build_index(csv_file=None):
    if csv_file is None:
        csv_file = os.path.join(os.path.dirname(__file__), 'ph_coords', 'ncr.csv')
    index = {}
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                city = row[0].strip().lower()
                lat = float(row[1].strip())
                lon = float(row[2].strip())
                index[city] = (lat, lon)
    except Exception as e:
        logging.error(f"Exception occurred while reading the CSV file: {e}")
    return index

# Get coordinates for a given city and province from the index
def get_coordinates(city, province, index):
    city_lower = city.lower()
    if city_lower in index:
        lat, lon = index[city_lower]
        return lat, lon
    else:
        logging.warning(f"No coordinates found for city '{city}' in province '{province}'.")
        return None

# Load API URLs from a JSON file
def load_api_urls(json_file=os.path.join(os.path.dirname(__file__), 'api_urls.json')):
    with open(json_file, 'r') as file:
        data = json.load(file)
        return data

# Fetch weather data for a city and write to CSV
def process_city(city_name, province_name, index, api_urls_combined, writer):
    coordinates = get_coordinates(city_name, province_name, index)
    if coordinates:
        lat, lon = coordinates
        current_api_index = 0
        while True:
            temperature, humidity = get_weather(lat, lon, tuple([api_urls_combined[current_api_index]]))

            if temperature is not None and humidity is not None:
                heat_index = calculate_heat_index(temperature, humidity)
                writer.writerow([city_name.title(), temperature, humidity, heat_index])
                logging.info(f"Data for {city_name.title()} written to CSV.")
                break
            else:
                logging.warning(f"Failed to retrieve temperature or humidity data for {city_name.title()} using API index {current_api_index}.")
                current_api_index = (current_api_index + 1) % len(api_urls_combined)
                if current_api_index == 0:
                    logging.error("All APIs failed for this city. Moving to the next city.")
                    break
    else:
        logging.warning(f"No coordinates found for city '{city_name}' in province '{province_name}' or an error occurred.")

# Main function to run the program
def main():
    start_time = time.time()  # Start the timer
    configure()

    index = build_index()
    cities = list(index.keys())
    province_name = "Metro Manila"

    first_api_key = os.getenv('8d1e78cf8cf1cebde3880054184c98d6fa6bebbd')
    second_api_key = os.getenv('5b1f43e3032c79a417144ec27d00a1b80a20bb7')
    if not first_api_key or not second_api_key:
        logging.error("API keys not found. Please set environment variables.")
        return

    api_urls = load_api_urls()
    api_urls_combined = (
        [url.format(api_key=first_api_key, lat="{lat}", lon="{lon}") for url in api_urls['8d1e78cf8cf1cebde3880054184c98d6fa6bebbd']] +
        [url.format(api_key=second_api_key, lat="{lat}", lon="{lon}") for url in api_urls['5b1f43e3032c79a417144ec27d00a1b80a20bb7']] +
        api_urls['83db893235619e973fe241e51f0f59f9c31299ec']
    )

    # Write data to CSV in the root directory
    csv_file_path = os.path.join(root_dir, 'heat_index_data.csv')
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["City", "Temperature", "Humidity", "Heat Index"])

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_city, city_name, province_name, index, api_urls_combined, writer) for city_name in cities]
            for future in as_completed(futures):
                future.result()

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time
    logging.info(f"Total time taken for the process to complete: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()