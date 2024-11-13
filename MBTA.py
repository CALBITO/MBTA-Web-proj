import requests
import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
TICKETMASTER_API_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

def get_lat_lng(place_name: str):
    """Get latitude and longitude from Mapbox API."""
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{quote(place_name)}.json?access_token={MAPBOX_TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['features']:
            latitude = data['features'][0]['geometry']['coordinates'][1]
            longitude = data['features'][0]['geometry']['coordinates'][0]
            return latitude, longitude
    return None, None

def get_nearest_stations(latitude: float, longitude: float, limit=3):
    """Get nearest MBTA stations using the MBTA API."""
    url = f"https://api-v3.mbta.com/stops?filter[latitude]={latitude}&filter[longitude]={longitude}&api_key={MBTA_API_KEY}"
    response = requests.get(url)
    stations = []
    if response.status_code == 200:
        data = response.json()
        for stop in data['data'][:limit]:  # Limit the number of stations returned
            station_name = stop['attributes']['name']
            accessible = stop['attributes']['wheelchair_boarding']
            stations.append((station_name, accessible == 1))
    return stations

def get_weather(latitude: float, longitude: float):
    """Get weather information from OpenWeather API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=imperial"
    response = requests.get(url)
    weather_description = "No data"
    weather = {}
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        weather = {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure']
        }
    return weather, weather_description

def get_ticketmaster_events(place_name: str):
    """Get nearby events from Ticketmaster API."""
    url = f"{TICKETMASTER_API_URL}?keyword={place_name}&apikey={TICKETMASTER_API_KEY}"
    response = requests.get(url)
    events = []
    if response.status_code == 200:
        data = response.json()
        events = data.get('_embedded', {}).get('events', [])  # Safely access the '_embedded' field
    return events
