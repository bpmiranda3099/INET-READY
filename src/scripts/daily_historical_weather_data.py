import os
import csv
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
log_file_path = os.path.join(root_dir, 'logs', 'historical_weather_data.log')

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

def get_recent_date():
    recent_date = (datetime.today() - timedelta(days=3)).strftime("%Y-%m-%d")
    return recent_date

def append_rows_to_city_end(rows_by_city, row):
    # row[0] is the city name
    if row[0] not in rows_by_city:
        rows_by_city[row[0]] = []
    rows_by_city[row[0]].append(row)

def read_rows_by_city(csv_file_path):
    rows_by_city = {}
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                city = row[0]
                if city not in rows_by_city:
                    rows_by_city[city] = []
                rows_by_city[city].append(row)
    return rows_by_city

def write_all_rows(csv_file_path, header, rows_by_city):
    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for city in rows_by_city:
            for row in rows_by_city[city]:
                writer.writerow(row)

def update_historical_weather_data():
    try:
        start_time = time.time()  # Start the timer

        # Read the city coordinates from the specified location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        input_file = os.path.join(script_dir, '..', '..', 'public', 'data', 'city_coords.csv')
        logger.info(f'Reading input file from {input_file}')
        with open(input_file, mode='r') as file:
            reader = csv.DictReader(file)
            cities = [row for row in reader]
            
            # Log the first city to check the structure
            if cities:
                logger.info(f'Sample city data: {cities[0]}')

        # Prepare the output CSV file in the public/data directory
        output_file = os.path.join(script_dir, '..', '..', 'public', 'data', 'historical_weather_data.csv')
        logger.info(f'Preparing output file at {output_file}')

        # Load existing rows
        existing_rows_by_city = read_rows_by_city(output_file)

        all_data_to_write = []

        # Base URL for the API
        base_url = "https://archive-api.open-meteo.com/v1/archive"

        # Batch processing cities
        batch_size = 10
        for i in range(0, len(cities), batch_size):
            batch_cities = cities[i:i + batch_size]  # Fixed: Use slicing, not indexing
            logger.info(f'Processing batch: {i // batch_size + 1}')

            for city_data in batch_cities:
                try:
                    # Access city data using dictionary keys from the CSV
                    # The keys should match the header in city_coords.csv
                    city_name = city_data.get('City')
                    latitude = city_data.get('Latitude')
                    longitude = city_data.get('Longitude')
                    
                    # Check if we have valid data
                    if not all([city_name, latitude, longitude]):
                        logger.warning(f'Missing data in city record: {city_data}')
                        continue
                        
                    logger.info(f'Processing city: {city_name}')

                    # Define the date range for the past two years
                    end_date = get_recent_date()
                    start_date = get_recent_date()
                    logger.info('Date range set')

                    # Fetch weather data with updated parameters to match new API URL structure
                    params = {
                        "latitude": latitude,
                        "longitude": longitude,
                        "start_date": start_date,
                        "end_date": end_date,
                        "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "wind_speed_10m_max", "shortwave_radiation_sum"],
                        "temperature_unit": "fahrenheit",
                        "timezone": "Asia/Singapore"
                    }

                    # Fetch weather data using the new base URL
                    responses = openmeteo.weather_api(base_url, params=params)

                    # Process the response
                    if responses:
                        response = responses[0]
                        daily = response.Daily()
                        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
                        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
                        daily_apparent_temperature_max = daily.Variables(2).ValuesAsNumpy()
                        daily_apparent_temperature_min = daily.Variables(3).ValuesAsNumpy()  
                        daily_wind_speed_10m_max = daily.Variables(4).ValuesAsNumpy() 
                        daily_shortwave_radiation_sum = daily.Variables(5).ValuesAsNumpy() 

                        daily_data = {
                            "date": pd.date_range(
                                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                                freq=pd.Timedelta(seconds=daily.Interval()),
                                inclusive="left"
                            )
                        }
                        daily_data["city"] = city_name  # Use city_name instead of city
                        daily_data["temperature_2m_max"] = daily_temperature_2m_max
                        daily_data["temperature_2m_min"] = daily_temperature_2m_min
                        daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
                        daily_data["apparent_temperature_mean"] = daily_apparent_temperature_min  
                        daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max 
                        daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum

                        daily_dataframe = pd.DataFrame(data=daily_data)

                        def validate_row(row):
                            # Ensure all required fields are present and not None
                            required_fields = ['city', 'date', 'temperature_2m_max', 'temperature_2m_min', 'apparent_temperature_max', 'apparent_temperature_mean', 'wind_speed_10m_max', 'shortwave_radiation_sum']
                            for field in required_fields:
                                if pd.isna(row[field]):
                                    return False
                            return True

                        for index, row in daily_dataframe.iterrows():
                            if validate_row(row):
                                row['date'] = get_recent_date()
                                heat_index = calculate_heat_index(row['temperature_2m_max'], row['apparent_temperature_mean'])
                                new_row = [row['city'], row['date'], row['temperature_2m_max'], row['temperature_2m_min'], row['apparent_temperature_max'], row['apparent_temperature_mean'], row['wind_speed_10m_max'], row['shortwave_radiation_sum'], heat_index]
                                city_name = new_row[0]
                                if city_name not in existing_rows_by_city:
                                    existing_rows_by_city[city_name] = []
                                existing_rows_by_city[city_name].append(new_row)
                            else:
                                logger.warning(f'Invalid data found in row {index}')
                except Exception as e:
                    logger.error(f'Error processing city data: {city_data}: {e}')

        header = ['City', 'Date', 'Temperature Max', 'Temperature Min', 'Apparent Temperature Max',
                  'Apparent Temperature Mean', 'Wind Speed', 'Solar Radiation',
                  'Heat Index']
        write_all_rows(output_file, header, existing_rows_by_city)

        elapsed_time = time.time() - start_time  # Calculate elapsed time
        logger.info(f'Total time taken for the process to complete: {elapsed_time:.2f} seconds')

    except Exception as e:
        logger.error(f'Error in main processing: {e}')

update_historical_weather_data()