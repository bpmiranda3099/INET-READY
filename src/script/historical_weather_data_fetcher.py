import os
import csv
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests
from loguru import logger
from functools import lru_cache
import time

# Define the root directory and log file path
root_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(root_dir, 'logs', 'historical_weather_data_fetcher.log')

# Configure the logger to write to the log file
logger.remove()  # Remove the default logger
logger.add(log_file_path, rotation="10 MB")  # Add a file handler with rotation

# Function to calculate heat index with LRU cache
@lru_cache(maxsize=1024)
def calculate_heat_index(temperature_c, humidity):
    if pd.isna(temperature_c) or pd.isna(humidity):
        return None
    temperature_f = (temperature_c * 9/5) + 32
    heat_index_f = (-42.379 + 2.04901523 * temperature_f + 10.14333127 * humidity 
                    - 0.22475541 * temperature_f * humidity - 0.00683783 * temperature_f**2 
                    - 0.05481717 * humidity**2 + 0.00122874 * temperature_f**2 * humidity 
                    + 0.00085282 * temperature_f * humidity**2 - 0.00000199 * temperature_f**2 * humidity**2)
    heat_index_c = (heat_index_f - 32) * 5/9
    return heat_index_c

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Function to write a single row to the CSV
def write_row_to_csv(row, csv_writer):
    csv_writer.writerow(row)

# Function to write data to CSV using ThreadPoolExecutor
def write_data_to_csv(data, csv_file_path):
    with open(csv_file_path, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        with ThreadPoolExecutor(max_workers=5) as executor:
            for row in data:
                executor.submit(write_row_to_csv, row, csv_writer)

try:
    start_time = time.time()  # Start the timer

    # Read the cavite.csv file
    input_file = os.path.join(os.path.dirname(__file__), 'ph_coords', 'cavite.csv')
    logger.info('Reading input file')
    with open(input_file, mode='r') as file:
        reader = csv.DictReader(file)
        cities = [row for row in reader]

    # Prepare the output CSV file (this will replace all existing data)
    date_today = datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(os.path.dirname(__file__), 'data', 'historical_weather_data', f'{date_today}_weather_data.csv')
    logger.info('Preparing output file')
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Place', 'Date', 'Temperature Max', 'Temperature Min', 'Apparent Temperature Max', 'Apparent Temperature Mean', 'Precipitation', 'Wind Speed Max', 'Solar Radiation', 'Heat Index'])

        all_data_to_write = []

        # Load the API URLs from the JSON file
        api_urls_file = os.path.join(os.path.dirname(__file__), 'api_urls.json')
        with open(api_urls_file, 'r') as f:
            api_urls = json.load(f)

        # Get the URL for the historical weather data
        historical_weather_url = api_urls["e1676fc69e2d521edf5539676a411dabd65bf2ca"][0]

        # Batch processing cities
        batch_size = 10
        for i in range(0, len(cities), batch_size):
            batch_cities = cities[i:i + batch_size]
            logger.info(f'Processing batch: {i // batch_size + 1}')

            for city in batch_cities:
                try:
                    place = city['Place']
                    latitude = city['Latitude']
                    longitude = city['Longitude']
                    logger.info(f'Processing city: {place}')

                    # Define the date range for the past two years
                    end_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=2*365 + 3)).strftime('%Y-%m-%d')
                    logger.info('Date range set')

                    # Fetch weather data for the date range
                    params = {
                        "latitude": latitude,
                        "longitude": longitude,
                        "start_date": start_date,
                        "end_date": end_date,
                        "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_mean", "rain_sum", "wind_speed_10m_max", "shortwave_radiation_sum"],
                        "timezone": "auto"
                    }

                    # Fetch weather data for the date range using the URL from the JSON file
                    responses = openmeteo.weather_api(historical_weather_url, params=params)

                    # Process the response
                    if responses:
                        response = responses[0]
                        daily = response.Daily()
                        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
                        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
                        daily_apparent_temperature_max = daily.Variables(2).ValuesAsNumpy()
                        daily_apparent_temperature_mean = daily.Variables(3).ValuesAsNumpy()
                        daily_rain_sum = daily.Variables(4).ValuesAsNumpy()
                        daily_wind_speed_10m_max = daily.Variables(5).ValuesAsNumpy()
                        daily_shortwave_radiation_sum = daily.Variables(6).ValuesAsNumpy()

                        daily_data = {
                            "date": pd.date_range(
                                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                                freq=pd.Timedelta(seconds=daily.Interval()),
                                inclusive="left"
                            )
                        }
                        daily_data["place"] = place
                        daily_data["temperature_2m_max"] = daily_temperature_2m_max
                        daily_data["temperature_2m_min"] = daily_temperature_2m_min
                        daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
                        daily_data["apparent_temperature_mean"] = daily_apparent_temperature_mean
                        daily_data["rain_sum"] = daily_rain_sum
                        daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
                        daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum

                        daily_dataframe = pd.DataFrame(data=daily_data)

                        def validate_row(row):
                            # Ensure all required fields are present and not None
                            required_fields = ['place', 'date', 'temperature_2m_max', 'temperature_2m_min', 'apparent_temperature_max', 'apparent_temperature_mean', 'rain_sum', 'wind_speed_10m_max', 'shortwave_radiation_sum']
                            for field in required_fields:
                                if pd.isna(row[field]):
                                    return False
                            return True

                        for index, row in daily_dataframe.iterrows():
                            if validate_row(row):
                                heat_index = calculate_heat_index(row['temperature_2m_max'], row['apparent_temperature_mean'])
                                all_data_to_write.append([row['place'], row['date'], row['temperature_2m_max'], row['temperature_2m_min'], row['apparent_temperature_max'], row['apparent_temperature_mean'], row['rain_sum'], row['wind_speed_10m_max'], row['shortwave_radiation_sum'], heat_index])
                            else:
                                logger.warning(f'Invalid data found in row {index}')
                except Exception as e:
                    logger.error(f'Error processing city {place}: {e}')

        if all_data_to_write:
            write_data_to_csv(all_data_to_write, output_file)
        else:
            logger.warning('No valid data found for the given places')

    elapsed_time = time.time() - start_time  # Calculate elapsed time
    logger.info(f'Total time taken for the process to complete: {elapsed_time:.2f} seconds')

except Exception as e:
    logger.error(f'Error in main processing: {e}')
