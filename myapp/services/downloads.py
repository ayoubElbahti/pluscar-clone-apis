import requests

# Define the regions
regions = ["America"]

# Create a dictionary to store tables for each region
region_tables = {}

# Loop through each region
for region in regions:
    # Define the URL to get countries for the current region
    url = f"https://api.first.org/data/v1/countries?region={region}"
    
    # Make the GET request
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        print(data)
        

    else:
        print(f"Failed to retrieve data for region {region}: {response.status_code}")

# Print the tables for each region

