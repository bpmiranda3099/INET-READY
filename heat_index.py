import csv
import requests
from requests.adapters import HTTPAdapter
import ssl
from dotenv import load_dotenv
import os

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

# Fetch weather data from the API
def get_weather(lat, lon, api_url):
    try:
        response = requests.get(api_url.format(lat=lat, lon=lon))
        response.raise_for_status()
        data = response.json()
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        return temperature, humidity
    except requests.exceptions.RequestException as e:
        print(f"Exception occurred while fetching data: {e}")
        return None, None

# Build an index of city coordinates from a CSV file
def build_index(csv_file=None):
    if csv_file is None:
        csv_file = 'C:/Users/brand/OneDrive - Lyceum of the Philippines University/Projects/INET-READY/ph_coords/ncr.csv'
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
        print(f"Exception occurred while reading the CSV file: {e}")
    return index

# Get coordinates for a given city and province from the index
def get_coordinates(city, province, index):
    city_lower = city.lower()
    if city_lower in index:
        lat, lon = index[city_lower]
        return lat, lon
    else:
        print(f"No coordinates found for city '{city}' in province '{province}'.")
        return None

# Main function to run the program
def main():
    configure()

    index = build_index()
    cities = list(index.keys())

    print("Select a city by number:")
    for i, city in enumerate(cities, start=1):
        print(f"{i}. {city.title()}")

    try:
        choice = int(input("Enter the number of the city: "))
        if 1 <= choice <= len(cities):
            city_name = cities[choice - 1]
        else:
            print("Invalid choice. Exiting.")
            return
    except ValueError:
        print("Invalid input. Exiting.")
        return

    province_name = "Metro Manila"
    coordinates = get_coordinates(city_name, province_name, index)

    if coordinates:
        lat, lon = coordinates
        api_key = os.getenv('OWM_API_KEY')
        if not api_key:
            print("API key not found. Please set the OWM_API_KEY environment variable.")
            return

        api_url = f"http://api.openweathermap.org/data/2.5/weather?lat={{lat}}&lon={{lon}}&appid={api_key}&units=metric"
        temperature, humidity = get_weather(lat, lon, api_url)

        if temperature is not None and humidity is not None:
            heat_index = calculate_heat_index(temperature, humidity)
            print(f"Current temperature in {city_name.title()}, {province_name}: {temperature}°C")
            print(f"Current humidity in {city_name.title()}, {province_name}: {humidity}%")
            print(f"Current heat index in {city_name.title()}, {province_name}: {heat_index:.2f}°C")
        else:
            print("Failed to retrieve temperature or humidity data.")
    else:
        print(f"No coordinates found for city '{city_name}' in province '{province_name}' or an error occurred.")

if __name__ == "__main__":
    main()
