from flask import Flask, render_template, request, redirect, url_for
import os
import requests
from dotenv import load_dotenv
from urllib.parse import quote
from MBTA import get_lat_lng, get_nearest_stations, get_weather, get_ticketmaster_events

app = Flask(__name__)
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")
MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
MBTA_BASE_URL = "https://api-v3.mbta.com/stops"
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
TICKETMASTER_API_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

def get_json(url: str) -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return {}

@app.route("/", methods=["GET", "POST"])
def index():
    messages = []
    if request.method == "POST":
        place_name = request.form["place_name"]
        latitude, longitude = get_lat_lng(place_name)
        if latitude and longitude:
            return redirect(url_for('find_stops', place_name=place_name, latitude=latitude, longitude=longitude))
        else:
            messages.append("Location not found. Please try again.")
    return render_template("index.html", messages=messages)

@app.route("/find_stops", methods=["GET"])
def find_stops():
    place_name = request.args.get("place_name")
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")
    
    if latitude and longitude:
        stations = get_nearest_stations(latitude, longitude, limit=3)  # Limiting to 3 nearest stations
        weather, weather_description = get_weather(latitude, longitude)
        events = get_ticketmaster_events(place_name)  # Fetch events using the updated method
        
        if stations:
            return render_template("mbta_res.html", place_name=place_name, stations=stations,
                                   weather=weather, weather_description=weather_description, events=events)
        else:
            messages = ["No stations found. Please try again."]
            return render_template("index.html", messages=messages)
    else:
        messages = ["Location not found. Please try again."]
        return render_template("index.html", messages=messages)

if __name__ == "__main__":
    app.run(debug=True)
