import overpy
import csv
import os

# Initialize the Overpass API
api = overpy.Overpass()

# Define the Overpass query to get cities, towns, and villages in Cavite, Philippines, including Naic
query = """
[out:json];
area["ISO3166-2"="PH-CAV"];
(
    node(area)[place~"city|town"];
    node["name"="Naic"];
);
out body;
"""

# Execute the query
result = api.query(query)

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

# Get the absolute path of the current script's directory
script_dir = os.path.abspath(os.path.dirname(__file__))
output_file = os.path.join(script_dir, 'cavite.csv')

# Open the CSV file for writing
with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["Place", "Latitude", "Longitude"])

        # Write the place data, excluding specified places
        for node in result.nodes:
                place_name = node.tags.get("name", "n/a")
                if place_name not in exclude_places:
                        writer.writerow([place_name, node.lat, node.lon])

print(f"Data has been written to {output_file}")
