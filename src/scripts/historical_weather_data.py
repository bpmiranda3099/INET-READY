import os
import csv
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests
from loguru import logger
import time
from functions.calculate_heat_index import calculate_heat_index

# Define the root directory and log file path
root_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(root_dir, 'logs', 'historical_weather_data.log')

# Configure the logger to write to the log file
logger.remove()  # Remove the default logger
logger.add(log_file_path, rotation="10 MB")  # Add a file handler with rotation

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
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['City', 'Date', 'Temperature Max', 'Temperature Min', 'Apparent Temperature Max', 'Apparent Temperature Min', 'Wind Speed', 'Solar Radiation', 'Relative Humidity', 'Heat Index'])

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
                    end_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=2*365 + 3)).strftime('%Y-%m-%d')
                    logger.info('Date range set')

                    # Fetch weather data with updated parameters to match new API URL structure
                    params = {
                        "latitude": latitude,
                        "longitude": longitude,
                        "start_date": start_date,
                        "end_date": end_date,
                        "daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "wind_speed_10m_max", "shortwave_radiation_sum"],
                        "hourly": ["relative_humidity_2m"],
                        "temperature_unit": "celsius",
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

                        # Process hourly data
                        hourly = response.Hourly()
                        hourly_relative_humidity_2m = hourly.Variables(0).ValuesAsNumpy()

                        daily_data = {
                            "date": pd.date_range(
                                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                                freq=pd.Timedelta(seconds=daily.Interval()),
                                inclusive="left"
                            )
                        }
                        daily_data["city"] = city_name  
                        daily_data["temperature_2m_max"] = daily_temperature_2m_max
                        daily_data["temperature_2m_min"] = daily_temperature_2m_min
                        daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
                        daily_data["apparent_temperature_min"] = daily_apparent_temperature_min  
                        daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max 
                        daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum

                        # Process hourly data into daily averages
                        hourly_data = {
                            "date": pd.date_range(
                                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                                freq=pd.Timedelta(seconds=hourly.Interval()),
                                inclusive="left"
                            ),
                            "relative_humidity_2m": hourly_relative_humidity_2m
                        }
                        hourly_dataframe = pd.DataFrame(data=hourly_data)
                        hourly_dataframe['date'] = hourly_dataframe['date'].dt.date
                        daily_humidity = hourly_dataframe.groupby('date')['relative_humidity_2m'].mean().reset_index()
                        daily_humidity['date'] = pd.to_datetime(daily_humidity['date'])

                        daily_dataframe = pd.DataFrame(data=daily_data)
                        # Convert date to match with daily humidity format
                        daily_dataframe['date_key'] = daily_dataframe['date'].dt.date
                        daily_humidity['date_key'] = daily_humidity['date'].dt.date
                        # Merge daily data with humidity averages
                        daily_dataframe = pd.merge(daily_dataframe, daily_humidity[['date_key', 'relative_humidity_2m']], 
                                                on='date_key', how='left')
                        daily_dataframe.drop('date_key', axis=1, inplace=True)

                        def validate_row(row):
                            # Ensure all required fields are present and not None
                            required_fields = ['city', 'date', 'temperature_2m_max', 'temperature_2m_min', 'apparent_temperature_max', 'apparent_temperature_min', 'wind_speed_10m_max', 'shortwave_radiation_sum', 'relative_humidity_2m']
                            for field in required_fields:
                                if pd.isna(row[field]):
                                    return False
                            return True

                        for index, row in daily_dataframe.iterrows():
                            if validate_row(row):
                                heat_index = calculate_heat_index(row['temperature_2m_max'], row['apparent_temperature_min'])
                                all_data_to_write.append([row['city'], row['date'], row['temperature_2m_max'], row['temperature_2m_min'], row['apparent_temperature_max'], row['apparent_temperature_min'], row['wind_speed_10m_max'], row['shortwave_radiation_sum'], row['relative_humidity_2m'], heat_index])
                            else:
                                logger.warning(f'Invalid data found in row {index}')
                except Exception as e:
                    logger.error(f'Error processing city data: {city_data}: {e}')

        if all_data_to_write:
            write_data_to_csv(all_data_to_write, output_file)
        else:
            logger.warning('No valid data found for the given places')

    elapsed_time = time.time() - start_time  # Calculate elapsed time
    logger.info(f'Total time taken for the process to complete: {elapsed_time:.2f} seconds')

except Exception as e:
    logger.error(f'Error in main processing: {e}')