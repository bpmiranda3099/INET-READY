import overpy
import csv

# Initialize the Overpass API
api = overpy.Overpass()

# Define the Overpass query to get cities in NCR, Philippines
query = """
[out:json];
area["ISO3166-2"="PH-00"];
node(area)[place=city];
out body;
"""

# Execute the query
result = api.query(query)

# Open the CSV file for writing
with open('ncr.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(["City", "Latitude", "Longitude"])

    # Write the city data
    for node in result.nodes:
        writer.writerow([node.tags.get("name", "n/a"), node.lat, node.lon])

print("Data has been written to ncr.csv")