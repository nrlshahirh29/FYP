import firebase_admin
from firebase_admin import credentials, db
import googlemaps
from googleplaces import GooglePlaces
from geopy import distance
from geopy.geocoders import Nominatim
import requests
import json
# Initialize Firebase Admin SDK
cred = credentials.Certificate(r'C:\Users\Dell\Documents\Jan24\fyp\All_code\built-environment-3005c-firebase-adminsdk-93gh1-cb883b3fca.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://built-environment-3005c-default-rtdb.firebaseio.com'
})

# Reference to your Firebase Realtime Database
ref = db.reference("Spreadsheet")

# Set up Google Maps API client
gmaps = googlemaps.Client(key='AIzaSyADSu3cWV6Vj4Tm65Oxc9dGBq1KRsoTtGo')  # Replace with your actual API key

# Set up Google Places API client

places_api_key = 'AIzaSyADSu3cWV6Vj4Tm65Oxc9dGBq1KRsoTtGo'  # Replace with your actual API key
google_places = GooglePlaces(places_api_key)
base_url = "https://places.googleapis.com/v1/places:searchNearby"
headers = {'Content-Type': 'application/json', 'X-Goog-Api-Key': 'AIzaSyADSu3cWV6Vj4Tm65Oxc9dGBq1KRsoTtGo','X-Goog-FieldMask': 'places.formattedAddress,places.nationalPhoneNumber,\
places.displayName.text,places.types,places.servesBeer,places.servesBreakfast,places.servesBrunch,places.servesCocktails,places.servesCoffee,\
places.servesDinner,places.servesLunch,places.servesVegetarianFood,places.servesWine,\
places.takeout,places.dineIn,\
places.plus_code'}

def get_lat_long(place_name, address):
    try:
        geocode_result = gmaps.geocode(f"{place_name}, {address}")
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
    except Exception as e:
        print(f"Error occurred during geocoding: {e}")
    return None, None
    
def calculate_distance(origin_lat, origin_lng, dest_lat, dest_lng):
    directions = gmaps.directions(
        (origin_lat, origin_lng), 
        (dest_lat, dest_lng), 
        mode="walking", 
        units="metric"  # Request distance in metric units (meters and kilometers)
    )

    if directions:
        # Extract the distance in meters from the directions response
        distance_meters = directions[0]['legs'][0]['distance']['value']

        # Convert meters to kilometers
        distance_km = distance_meters / 1000.0

        # Format and return the distance in kilometers with two decimal places
        return f"{distance_km:.2f}"
    else:
        return "Error fetching directions."

def update_data(patient_id, key, subkey, data):
    ref.child("Places").child(key).child(str(patient_id)).set(data)

def restaurant(i, latitude, longitude):
    restaurant_data = []
    r = requests.post(base_url, headers=headers, json={
        "includedTypes": ["restaurant","cafe","bakery","bar","sandwich_shop","coffee_shop","ice_cream_shop","steak_house"],
        "locationRestriction": {
            "circle": {
                "center": {
                "latitude": latitude,
                "longitude": longitude
            },
        "radius": 5000.0
        }
        } 
    })

    data = json.loads(r.text)

    # Iterate over each restaurant and store its information in Firebase
    for place in data.get('places', []):
        restaurant_name = place.get('displayName', {}).get('text', 'Restaurant Name not available')
        types_array = place.get('types', [])
        # Extract the first element from the types array
        restaurant_types = types_array[0] if types_array else 'Type not available'
        
        
        if place.get('nationalPhoneNumber'):
            phone_number = place['nationalPhoneNumber']
        
        serves_breakfast = 'Not Serve'
        if place.get('servesBreakfast'): 
            serves_breakfast = 'Serve'
        
        serves_brunch = 'Not Serve'
        if place.get('servesBrunch'): 
            serves_brunch = 'Serve'

        serves_lunch = 'Not Serve'
        if place.get('servesLunch'): 
            serves_lunch = 'Serve'
        
        serves_dinner = 'Not Serve'
        if place.get('servesDinner'): 
            serves_dinner = 'Serve'
        
        serves_vegan = 'Not Serve'
        if place.get('servesVegan'): 
            serves_vegan = 'Serve'
        
        serves_beer = 'Not Serve'
        if place.get('servesBeer'): 
            serves_beer = 'Serve'

        serves_wine = 'Not Serve'
        if place.get('servesWine'): 
            serves_wine = 'Serve'

        takeout = 'Not available'
        if place.get('takeout'): 
            takeout = 'Available'    
        
        dinein = 'Not available'
        if place.get('dineIn'): 
            dinein = 'Available'  

        #url = place[websiteUri]
        # print(place['formattedAddress'])
        address = place['formattedAddress']

        place_latitude, place_longitude = get_lat_long(restaurant_name, address)
        distance = None
        distance = calculate_distance(latitude, longitude, place_latitude, place_longitude)

        # Store restaurant information in Firebase under the patient's ID with a numerical identifier
        restaurant_data.append({
            'ID' : i,
            'Name': restaurant_name,
            'Types': restaurant_types,
            'Phone Number': phone_number,
            'Serves Breakfast': serves_breakfast,
            'Serves Lunch': serves_lunch,
            'Serves Brunch': serves_brunch,
            'Serves Dinner': serves_dinner,
            'Serves Vegetarian Food': serves_vegan,
            'Serves Beers': serves_beer,
            'Serves Wine': serves_wine,
            'Takeout': takeout,
            'Dine-in': dinein,
           # 'URL': url,
            'Address': address,
            "latitude": latitude,
            "longitude": longitude,
            "distance in km": distance
        })
    update_data(i, "Restaurant", None, restaurant_data)

    print(f"{len(restaurant_data)} restaurants information stored for patient {i}.")

def mall(i, latitude, longitude):
    
    grocery_data = []
    r = requests.post(base_url, headers=headers, json={
        "includedTypes": ["store","market","supermarket","wholesaler","shopping_mall"],
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": 5000.0
            }
        }
    })

    data = json.loads(r.text)
    
    # Iterate over each grocery store and store its information in Firebase
    for place in data.get('places', []):
        grocery_name = place.get('displayName', {}).get('text', 'Grocery Name not available')
        address = place.get('formattedAddress', 'Address not available')
        types_array = place.get('types', [])
        # Extract the first element from the types array
        mall_type= types_array[0] if types_array else 'Type not available'
        place_latitude, place_longitude = get_lat_long(grocery_name, address)
        distance = None
        distance = calculate_distance(latitude, longitude, place_latitude, place_longitude)
        grocery_types = types_array[0] if types_array else 'Type not available'
        
        grocery_data.append({
            'ID': i,
            'Name': grocery_name,
            'Address': address,
            "latitude": latitude,
            "longitude": longitude,
            "distance in km": distance
            
        })
    
    update_data(i, "Shopping", None, grocery_data)
    
    print(f"{len(grocery_data)} Grocery information stored for patient {i}.")

def health(i, latitude, longitude):
    health_data = []
    r = requests.post(base_url, headers=headers, json={
        "includedTypes": ["dental_clinic","dentist","doctor","drugstore","hospital","medical_lab","pharmacy","physiotherapist"],
        "locationRestriction": {
            "circle": {
                "center": {
                "latitude": latitude,
                "longitude": longitude
            },
      "radius": 5000.0
        }
        } 
    })

    data = json.loads(r.text)
    
    # Iterate over each grocery store and store its information in Firebase
    for place in data.get('places', []):
        hospital_name = place.get('displayName', {}).get('text', 'Hospital Name not available')
        address = place['formattedAddress']
        place_latitude, place_longitude = get_lat_long(hospital_name, address)

        if place.get('nationalPhoneNumber'):
            phone_number = place['nationalPhoneNumber']

        distance = None
        distance = calculate_distance(latitude, longitude, place_latitude, place_longitude)
        types_array = place.get('types', [])
        health_types = types_array[0] if types_array else 'Type not available'


        health_data.append({
            'ID' : i,
            'Name': hospital_name,
            'Address': address,
            'Phone Number' : phone_number,
            "latitude": latitude,
            "longitude": longitude,
            "distance in km": distance
        
        })
    update_data(i, "Health", None, health_data)

    print(f"{len(health_data)} Hospital information stored for patient {i}.")

def recreational(i, latitude, longitude):
    recreational_data = []
    r = requests.post(base_url, headers=headers, json={
        "includedTypes": ["bowling_alley","community_center","cultural_center","dog_park","event_venue","hiking_area","marina","park","tourist_attraction","zoo"],
        "locationRestriction": {
            "circle": {
                "center": {
                "latitude": latitude,
                "longitude": longitude
            },
      "radius": 5000.0
        }
        }
    })

    data = json.loads(r.text)
    # Add debugging information to check the API response
    #print(f"Response from API for mall search: {data}")
    # Iterate over each grocery store and store its information in Firebase
    for place in data.get('places', []):
        types_array = place.get('types', [])
        recreational_name = place.get('displayName', {}).get('text', 'Recreational name not available')
        address = place['formattedAddress']
        acitivity_types = types_array[0] if types_array else 'Type not available'
        place_latitude, place_longitude = get_lat_long(recreational_name, address)
        distance = None
        distance = calculate_distance(latitude, longitude, place_latitude, place_longitude)

        recreational_data.append({
            'ID' : i,
            'Name': recreational_name,
            'Address': address,
            "latitude": latitude,
            "longitude": longitude,
            "distance in km":distance
            
        })
    update_data(i, "Recreational", None, recreational_data)

    print(f"{len(recreational_data)} Recreational information stored for patient {i}.")

def sports(i, latitude, longitude):
    sports_data = []
    r = requests.post(base_url, headers=headers, json={
        "includedTypes": ["athletic_field","fitness_center","golf_course","gym","playground","sports_club","sports_complex","stadium","swimming_pool"],
        "locationRestriction": {
            "circle": {
                "center": {
                "latitude": latitude,
                "longitude": longitude
            },
      "radius": 5000.0
        }
        } 
    })

    data = json.loads(r.text)
  
    # Iterate over each grocery store and store its information in Firebase
    for place in data.get('places', []):
        sports_name = place.get('displayName', {}).get('text', 'Sports Name not available')
        address = place['formattedAddress']
        types_array = place.get('types', [])

        place_latitude, place_longitude = get_lat_long(sports_name, address)
        distance = None
        distance = calculate_distance(latitude, longitude, place_latitude, place_longitude)

        sports_types = types_array[0] if types_array else 'Type not available'
        sports_data.append({
            'ID' : i,
            'Name': sports_name,
            'Address': address,
            "latitude": latitude,
            "longitude": longitude,
            "distance in km": distance
        })
    update_data(i, "Sports", None, sports_data)

    print(f"{len(sports_data)} Sports information stored for patient {i}.")

def transport(i, latitude, longitude):
    transport_data = []
    r = requests.post(base_url, headers=headers, json={
        "includedTypes": ["bus_stop","ferry_terminal","light_rail_station","park_and_ride","subway_station","taxi_stand","train_station","transit_depot","transit_station"],
        "locationRestriction": {
            "circle": {
                "center": {
                "latitude": latitude,
                "longitude": longitude
            },
      "radius": 5000.0
        }
        } 
    })

    data = json.loads(r.text)
    
    # Iterate over each grocery store and store its information in Firebase
    for place in data.get('places', []):
        transport_name = place.get('displayName', {}).get('text', 'Transport Name not available')
        address = place['formattedAddress']
        types_array = place.get('types', [])
        place_latitude, place_longitude = get_lat_long(transport_name, address)
    
        distance = None

        distance = calculate_distance(latitude, longitude, place_latitude, place_longitude)
        transport_types = types_array[0] if types_array else 'Type not available'


        transport_data.append({
            'ID' : i,
            'Name': transport_name,
            'Address' : address,
            "latitude": latitude,
            "longitude": longitude,
            "distance in km": distance
            
            
        })
    update_data(i, "Transportation", None, transport_data)

    print(f"{len(transport_data)} Transportation information stored for patient {i}.")

def worship(i, latitude, longitude):
    worship_data = []
    r = requests.post(base_url, headers=headers, json={
        "includedTypes": ["church","hindu_temple","mosque"],
        "locationRestriction": {
            "circle": {
                "center": {
                "latitude": latitude,
                "longitude": longitude
            },
      "radius": 5000.0
        }
        } 
    })

    data = json.loads(r.text)
  
    # Iterate over each grocery store and store its information in Firebase
    for place in data.get('places', []):
        worship__name = place.get('displayName', {}).get('text', 'Worship place name not available')
        address = place['formattedAddress']
        types_array = place.get('types', [])
        place_latitude, place_longitude = get_lat_long(worship__name, address)
        distance = None
        
        distance = calculate_distance(latitude, longitude, place_latitude, place_longitude)
        worship_types = types_array[0] if types_array else 'Type not available'
        worship_data.append({
            'ID' : i,
            'Name': worship__name,
            'Address': address,
            "latitude": latitude,
            "longitude": longitude,
            "distance in km": distance
           
        })
    update_data(i, "Worship", None, worship_data)

    print(f"{len(worship_data)} Worship information stored for patient {i}.")

def govern(i, latitude, longitude):
    govern_data = []
    r = requests.post(base_url, headers=headers, json={
        "includedTypes": ["city_hall","courthouse","embassy","fire_station","local_government_office","police","post_office"],
        "locationRestriction": {
            "circle": {
                "center": {
                "latitude": latitude,
                "longitude": longitude
            },
      "radius": 5000.0
        }
        } 
    })

    data = json.loads(r.text)
  
    # Iterate over each grocery store and store its information in Firebase
    for place in data.get('places', []):
        govern_name = place.get('displayName', {}).get('text', 'Government place name not available')
        address = place['formattedAddress']
        
        place_latitude, place_longitude = get_lat_long(govern_name, address)
        distance = None
        
        distance = calculate_distance(latitude, longitude, place_latitude, place_longitude)
    
        govern_data.append({
            'ID' : i,
            'Name': govern_name,
            'Address': address,
            "latitude": latitude,
            "longitude": longitude,
            "distance in km": distance

        })
    update_data(i, "Government", None, govern_data)

    print(f"{len(govern_data)} Government information stored for patient {i}.")

def services(i, latitude, longitude):
    services_data = []
    r = requests.post(base_url, headers=headers, json={
        "includedTypes": ["barber_shop","beauty_salon","cemetery","child_care_agency","consultant","courier_service","electrician","florist","funeral_home","hair_care","hair_salon","insurance_agency","laundry","lawyer","locksmith","moving_company","painter","plumber","real_estate_agency","roofing_contractor","storage","tailor","telecommunications_service_provider","travel_agency","veterinary_care"],
        "locationRestriction": {
            "circle": {
                "center": {
                "latitude": latitude,
                "longitude": longitude
            },
      "radius": 5000.0
        }
        } 
    })

    data = json.loads(r.text)
  
    # Iterate over each grocery store and store its information in Firebase
    for place in data.get('places', []):
        services_name = place.get('displayName', {}).get('text', 'Services place name not available')
        address = place['formattedAddress']

        place_latitude, place_longitude = get_lat_long(services_name, address)
        
        distance = None
       
        distance = calculate_distance(latitude, longitude, place_latitude, place_longitude)
    
        services_data.append({
            'ID' : i,
            'Name': services_name,
            'Address': address,
            "latitude": latitude,
            "longitude": longitude,
            "distance in km": distance
            
        })
    update_data(i, "Services", None, services_data)

    print(f"{len(services_data)} Services information stored for patient {i}.")

def process_patients():
    
    # Get a reference to the "SpreadSheet" node in your Firebase database
    spreadsheet_ref = db.reference("SpreadSheet")
    # Retrieve all the patients from the Firebase database
    patients = spreadsheet_ref.get()

    if patients:
        for patient_data in patients:
            if isinstance(patient_data, dict):
                patient_name = patient_data.get("Name")
                patient_address = patient_data.get("Address")
                patient_ID = patient_data.get("ID")
                if patient_name and patient_address and patient_ID:
                    print(f"Processing data for patient {patient_name}, Address: {patient_address}, ID: {patient_ID}")
                    # Geocode the address to obtain latitude and longitude
                    geocode_result = gmaps.geocode(patient_address)
                    if geocode_result:
                        location = geocode_result[0]['geometry']['location']
                        latitude = location['lat']
                        longitude = location['lng']
                        print(latitude, longitude)

                        restaurant(patient_ID, latitude, longitude)
                        health(patient_ID, latitude, longitude)
                        mall(patient_ID, latitude, longitude)
                        recreational(patient_ID, latitude, longitude)
                        sports(patient_ID, latitude, longitude)
                        transport(patient_ID, latitude, longitude)
                        services(patient_ID, latitude, longitude)
                        govern(patient_ID, latitude, longitude)
                        worship(patient_ID, latitude, longitude)
                        
                        # Add similar conditions for other keys if necessary
                        print()  # Add an empty line for clarity between different services
    
                    else:
                        print(f"Geocoding failed for address: {patient_address}")
                    
                else:
                    print("ID, Name, or Address key is missing or empty in patient data.")
            else:
                print("Skipping invalid data for a patient.")
    else:
        print("No patient data found in the database.")

# Call the process_patients function to start processing the data
process_patients()