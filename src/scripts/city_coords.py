import overpy
import csv
import os
from loguru import logger

# Define the root directory and log file path
root_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(root_dir, 'logs', 'historical_weather_data.log')
logger.add(log_file_path, rotation="10 MB", level="INFO")

logger.info("Starting city coordinates extraction")

# Initialize the Overpass API
api = overpy.Overpass()

# Define the Overpass query to get cities, towns, and villages in Cavite, Philippines, including Naic
query = """
[out:json];
area["ISO3166-2"="PH-CAV"];
(
    node(area)[place~"city|town"];
);
out body;
"""

logger.info("Executing Overpass API query for Cavite cities and towns")
# Execute the query
result = api.query(query)
logger.success(f"Query successful. Retrieved {len(result.nodes)} locations")

# List of places to exclude
exclude_places = [
        "Georgetown Heights Phase 2 & 3",
        "B17",
        "B1",
        "B11",
        "B12",
        "B3",
        "B4",
        "B5",
        "B8",
        "B9",
        "B13",
        "B14",
        "B15",
        "B10",
        "B16",
        "B2",
        "B1",
        "B6",
        "Zonaga Compound",
        "n/a",
        "Banal",
        "General Emilio Aguinaldo"
]

logger.info(f"Filtering out {len(exclude_places)} excluded places")

script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, '..', '..', 'public', 'data', 'city_coords.csv')
logger.info(f"Preparing to write data to {output_file}")

# Open the CSV file for writing
with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["City","Latitude", "Longitude"])
        
        included_count = 0
        # Write the place data, excluding specified places
        for node in result.nodes:
                place_name = node.tags.get("name", "n/a")
                if place_name not in exclude_places:
                        writer.writerow([place_name, node.lat, node.lon])
                        included_count += 1
                else:
                        logger.debug(f"Excluded place: {place_name}")

logger.success(f"Data has been written to {output_file}. Included {included_count} places.")
logger.info("Script completed successfully")
