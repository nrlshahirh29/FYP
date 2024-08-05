import gmplot
import pandas as pd
import googlemaps
from geopy import distance

apikey = 'AIzaSyADSu3cWV6Vj4Tm65Oxc9dGBq1KRsoTtGo'

# Load the Excel file into a DataFrame
df_poiAddress = pd.read_excel(r"C:\Users\Dell\Documents\Jan24\fyp\visual\latest.xlsx")
df_patientAddress = pd.read_excel(r"C:\Users\Dell\Documents\Jan24\fyp\visual\SpreadSheet.xlsx")

# Geocoding patient addresses into latitude
gmaps_key = googlemaps.Client(key=apikey)

def geocode(add):
    try:
        g = gmaps_key.geocode(add)
        if g:
            lat = g[0]["geometry"]["location"]["lat"]
            lng = g[0]["geometry"]["location"]["lng"]
            return lat, lng
        else:
            print(f"Geocode error: Address '{add}' could not be geocoded.")
            return None, None
    except Exception as e:
        print(f"Geocode error: {e} for address '{add}'")
        return None, None

# Clean the Value.Name column
df_poiAddress['Value.Name'] = df_poiAddress['Value.Name'].apply(lambda x: x.replace("'", ""))

# Concatenate Name and Address for POI
df_poiAddress['full_address'] = df_poiAddress['Value.Name'] + ', ' + df_poiAddress['Value.Address']

# Apply geocoding function
df_patientAddress['geocoded'] = df_patientAddress['Address'].apply(geocode)
df_poiAddress['geocoded'] = df_poiAddress['full_address'].apply(geocode)

# Filter out rows where geocoding failed
df_patientAddress = df_patientAddress[df_patientAddress['geocoded'].apply(lambda x: x is not None)]
df_poiAddress = df_poiAddress[df_poiAddress['geocoded'].apply(lambda x: x is not None)]

# Extract latitude and longitude
patientLats = [x[0] for x in df_patientAddress["geocoded"] if x is not None]
patientLngs = [x[1] for x in df_patientAddress["geocoded"] if x is not None]
patientIDs = df_patientAddress['ID']

patient_lat = df_poiAddress['Value.latitude']
patient_long = df_poiAddress['Value.longitude']


# Check and print the geocoded result for row 98
poiLats = [x[0] for x in df_poiAddress["geocoded"] if x is not None]
poiLngs = [x[1] for x in df_poiAddress["geocoded"] if x is not None]
poiNames = df_poiAddress['Name']
poiDist = df_poiAddress['Value.distance in km']
poiId = df_poiAddress['Value.ID']
poiType = df_poiAddress['Value.Types']  # Assuming 'type' column contains restaurant types

if poiLats and poiLngs:  # Check if poiLats is not empty
    min_lat, max_lat = min(poiLats), max(poiLats)
    min_lng, max_lng = min(poiLngs), max(poiLngs)

    # Calculate the bounding box
    polyCoor = [(min_lat, min_lng), (max_lat, min_lng), (max_lat, max_lng), (min_lat, max_lng)]

    # Separate latitude and longitude for polygon
    polyLats, polyLngs = zip(*polyCoor)

    # Create the map plotter
    gmap = gmplot.GoogleMapPlotter((min_lat + max_lat) / 2, (min_lng + max_lng) / 2, 14, apikey=apikey)

    # Define colors for different types of places
    type_colors = {
        'Transportation': 'black',
        'Services': '#40E0D0',
        'Government': '#EEE8AA',
        'Sports': '#F0FFFF',
        'Health': '#FFC0CB',
        'Recreational': 'purple',
        'Worship': '#228B22',
        'Shopping': '#FFFFFF',
        'Restaurant': 'orange'
    }


    # Plot patient addresses with labels
    for lat, lng, patient_id in zip(patientLats, patientLngs, patientIDs):
        gmap.marker(lat, lng, 'red', title=f"Patient ID: {patient_id}")

    # Plot other places without additional information
    for lat, lng, place_type, distance, place_id in zip(poiLats, poiLngs, poiNames, poiDist, poiId):
        if place_type not in ['Shopping', 'Restaurant', 'Worship']:
            color = type_colors.get(place_type, 'gray')  # Default to gray if type not found
            gmap.marker(lat, lng, color, title=f"{place_type}, ({lat}, {lng}), Distance: {distance} km, ID: {place_id}")

    # Plot grocery, restaurant, and worship places with additional information
    for lat, lng, place_type, poi_type, distance, place_id in zip(poiLats, poiLngs, poiNames, poiType, poiDist, poiId):
        if place_type in ['Shopping', 'Restaurant', 'Worship']:
            color = type_colors.get(place_type, 'gray')  # Default to gray if type not found
            gmap.marker(lat, lng, color, title=f"{place_type}, ({lat}, {lng}), Type: {poi_type}, Distance: {distance} km, ID: {place_id}")

    # Draw a bounding box
    gmap.polygon(polyLats, polyLngs, color='cornflowerblue', edge_width=10)

    # Draw the map
    gmap.draw(r'C:\Users\Dell\Documents\Jan24\fyp\visual\visual.html')

    print("map.html has been created successfully.")
else:
    print("No valid geocoded results for points of interest.")