import os
import time
import csv
import json
import ssl
import requests
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import mysql.connector
import mysql.connector.pooling
from loguru import logger
import logging

# Determine the root directory of the script
root_dir = os.path.dirname(os.path.abspath(__file__))

# Configure logging to append to heat_index_system.log in the specified directory
log_file = os.path.join(root_dir, 'logs', 'heat_index_system.log')
logger.add(log_file, level="INFO", format="{time} - {level} - {message}", rotation="10 MB", retention="10 days")
# Remove default console handler
logger.remove()

# Add a file handler
logger.add(log_file, level="INFO", format="{time} - {level} - {message}", rotation="10 MB", retention="10 days")

# Load environment variables from a .env file
def configure():
    load_dotenv()
    logger.info("Environment variables loaded.")

# Custom HTTPAdapter to lower SSL security level
class CustomHTTPAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        super().init_poolmanager(*args, **kwargs)
        logger.info("Custom HTTPAdapter initialized with lowered SSL security level.")

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
                logger.error(f"Exception occurred while fetching data from API: {sanitized_message}")
                if attempt < retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("Max retries reached. Moving to the next API.")
        if success:
            break
    return None, None

# Build an index of city coordinates from a CSV file
def build_index(csv_file=None):
    if csv_file is None:
        csv_file = os.path.join(os.path.dirname(__file__), 'ph_coords', 'cavite.csv')
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
        logger.error(f"Exception occurred while reading the CSV file: {e}")
    return index

# Get coordinates for a given city and province from the index
def get_coordinates(city, province, index):
    city_lower = city.lower()
    if city_lower in index:
        lat, lon = index[city_lower]
        return lat, lon
    else:
        logger.warning(f"No coordinates found for city '{city}' in province '{province}'.")
        return None

# Load API URLs from a JSON file
def load_api_urls(json_file=os.path.join(os.path.dirname(__file__), 'api_urls.json')):
    with open(json_file, 'r') as file:
        data = json.load(file)
        return data

# Fetch weather data for a list of cities and write to CSV
def process_cities(city_names, province_name, index, api_urls_combined, writer, conn_pool):
    weather_data = []
    for city_name in city_names:
        logger.info(f"Processing city: {city_name}")
        coordinates = get_coordinates(city_name, province_name, index)
        if coordinates:
            lat, lon = coordinates
            logger.info(f"Coordinates for {city_name}: Latitude {lat}, Longitude {lon}")
            current_api_index = 0
            while True:
                temperature, humidity = get_weather(lat, lon, tuple([api_urls_combined[current_api_index]]))

                if temperature is not None and humidity is not None:
                    logger.info(f"Weather data for {city_name}: Temperature {temperature}, Humidity {humidity}")
                    heat_index = calculate_heat_index(temperature, humidity)
                    weather_data.append((city_name.title(), temperature, humidity, heat_index))
                    logger.info(f"Data for {city_name.title()} written to CSV.")
                    break
                else:
                    logger.warning(f"Failed to retrieve temperature or humidity data for {city_name.title()} using API index {current_api_index}.")
                    current_api_index = (current_api_index + 1) % len(api_urls_combined)
                    if current_api_index == 0:
                        logger.error("All APIs failed for this city. Moving to the next city.")
                        break
        else:
            logger.warning(f"No coordinates found for city '{city_name}' in province '{province_name}' or an error occurred.")
    
    # Write all weather data to CSV
    for data in weather_data:
        writer.writerow(data)
    
    # Update the database with all weather data
    update_database(weather_data, conn_pool)

# Update the database with the new weather data in batches
def update_database(weather_data, conn_pool, retries=3, delay=5):
    conn = None
    for attempt in range(retries):
        try:
            conn = conn_pool.get_connection()
            cursor = conn.cursor()

            # Transfer previous data to weatherdatahistory table
            for data in weather_data:
                city, temperature, humidity, heat_index = data
                cursor.execute("SELECT temperature, humidity, heat_index, date_added, time_added FROM weatherdata WHERE city = %s", (city,))
                previous_data = cursor.fetchone()
                if previous_data:
                    previous_temperature, previous_humidity, previous_heat_index, previous_date_added, previous_time_added = previous_data
                    cursor.execute("""
                        INSERT INTO weatherdatahistory (city, temperature, humidity, heat_index, date_added, time_added)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (city, previous_temperature, previous_humidity, previous_heat_index, previous_date_added, previous_time_added))
                    
                    # Remove the previous data from weatherdatahistory table
                    cursor.execute("DELETE FROM weatherdata WHERE city = %s", (city,))

            # Update the weatherdata table with new data
            for data in weather_data:
                city, temperature, humidity, heat_index = data
                cursor.execute("""
                    INSERT INTO weatherdata (city, temperature, humidity, heat_index)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        temperature = VALUES(temperature),
                        humidity = VALUES(humidity),
                        heat_index = VALUES(heat_index)
                """, (city, temperature, humidity, heat_index))
            
            conn.commit()
            logger.info("Database updated for batch of cities.")
            break
        except mysql.connector.errors.PoolError as e:
            logger.error(f"PoolError occurred while getting connection from pool: {e}")
            if attempt < retries - 1:
                logger.info(f"Retrying database operation in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Max retries reached for database operation.")
        except mysql.connector.errors.OperationalError as e:
            logger.error(f"OperationalError occurred while updating the database: {e}")
            if attempt < retries - 1:
                logger.info(f"Retrying database operation in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("Max retries reached for database operation.")
                if conn:
                    conn.rollback()
        except Exception as e:
            logger.error(f"Exception occurred while updating the database: {e}")
            if conn:
                conn.rollback()
            break
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

# Function to insert weather data into the database
def insert_weather_data(city, temperature, humidity, heat_index):
    # Database connection
    connection = mysql.connector.connect(
        pool_name="mypool",
        pool_size=3,
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = connection.cursor()

    # Retrieve existing data from WeatherData table
    select_query = "SELECT city, temperature, humidity, heat_index, date_added, time_added FROM WeatherData WHERE city = %s"
    cursor.execute(select_query, (city,))
    existing_data = cursor.fetchone()

    if existing_data:
        # Insert existing data into weatherdatahistory table
        insert_history_query = """
        INSERT INTO weatherdatahistory (city, temperature, humidity, heat_index, date_added, time_added)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_history_query, existing_data)

        # Update WeatherData table with new data
        update_query = """
        UPDATE WeatherData
        SET temperature = %s, humidity = %s, heat_index = %s
        WHERE city = %s
        """
        cursor.execute(update_query, (temperature, humidity, heat_index, city))
    else:
        # Insert new data into WeatherData table
        insert_query = """
        INSERT INTO WeatherData (city, temperature, humidity, heat_index)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (city, temperature, humidity, heat_index))

    # Retrieve the current values from the weatherdata table
    select_query = """
        SELECT city, temperature, humidity, heat_index, date_added, time_added
        FROM weatherdata
        WHERE city = %s
    """
    cursor.execute(select_query, (city,))
    previous_values = cursor.fetchone()

    # Insert the previous values into the weatherdatahistory table
    insert_query_history = """
        INSERT INTO weatherdatahistory (city, temperature, humidity, heat_index, date_added, time_added)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query_history, previous_values)

    # Update the weatherdata table with the new values
    update_query = """
        UPDATE weatherdata
        SET temperature = %s, humidity = %s, heat_index = %s
        WHERE city = %s
    """
    cursor.execute(update_query, (temperature, humidity, heat_index, city))

    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    # Logging for debugging
    logger.info(f"Inserted/Updated weather data for city: {city}")

def setup_logging():
    logger = logging.getLogger()
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

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
        logger.error("API keys not found. Please set environment variables.")
        return

    api_urls = load_api_urls()
    api_urls_combined = (
        [url.format(api_key=first_api_key, lat="{lat}", lon="{lon}") for url in api_urls['8d1e78cf8cf1cebde3880054184c98d6fa6bebbd']] +
        [url.format(api_key=second_api_key, lat="{lat}", lon="{lon}") for url in api_urls['5b1f43e3032c79a417144ec27d00a1b80a20bb7']] +
        api_urls['83db893235619e973fe241e51f0f59f9c31299ec']
    )

    # Database connection pool
    conn_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=10,  # Increase pool size
        pool_reset_session=True,
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        connection_timeout=300
    )

    # Write data to CSV in the root directory
    csv_file_path = os.path.join(root_dir, 'data', 'heat_index_data.csv')
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["City", "Temperature", "Humidity", "Heat Index"])

        batch_size = 10
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_cities, cities[i:i + batch_size], province_name, index, api_urls_combined, writer, conn_pool) for i in range(0, len(cities), batch_size)]
            for future in as_completed(futures):
                future.result()

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time
    logger.info(f"Total time taken for the process to complete: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    setup_logging()
    main()
