from flask import Flask, jsonify, render_template, request
import requests
import os
from dotenv import load_dotenv

# ---------------------------------
# Load environment variables
# ---------------------------------
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("WEATHER_API_KEY")

LAT, LON = 32.8546, -79.9748


# ---------------------------------
# Cyclone Detection – Tropical API
# ---------------------------------
def is_there_any_storm_Bay_of_Bengal():
    url = "https://dev.tropicalinfo.com/api/storms"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return False

        storms = response.json()

        for storm in storms:
            lat = storm.get("lat")
            lon = storm.get("lon")

            if lat is not None and lon is not None:
                if 5 <= lat <= 22 and 80 <= lon <= 100:
                    return True

        return False

    except Exception as e:
        print("Cyclone API error:", e)
        return False


# ---------------------------------
# OpenWeather Alerts – Bay of Bengal
# ---------------------------------
def bay_of_bengal_alerts(openweather_api_key):
    if not openweather_api_key:
        return False

    lat, lon = 15.5, 90.0
    url = "https://api.openweathermap.org/data/2.5/onecall"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": openweather_api_key,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return False

        data = response.json()
        return bool(data.get("alerts"))

    except Exception as e:
        print("OpenWeather alert error:", e)
        return False


# ---------------------------------
# Home Page
# ---------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------
# Weather API
# ---------------------------------
@app.route("/weather")
def weather():
    if not API_KEY:
        return jsonify({"error": "WEATHER_API_KEY not found"}), 500

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": LAT,
        "lon": LON,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code != 200 or "main" not in data:
            return jsonify({"error": "Weather API failed"}), 500

        return jsonify({
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------
# Rain Probability Calculation
# ---------------------------------
@app.route("/rain", methods=["POST"])
def rain():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    temperature = data.get("temperature")
    humidity = data.get("humidity")

    if temperature is None or humidity is None:
        return jsonify({"error": "Missing temperature or humidity"}), 400

    rain_chance = 0

    # Rule 1: Humidity
    if humidity > 75:
        rain_chance += 23

    # Rule 2: Temperature
    if temperature > 16:
        rain_chance += 24

    # Rule 3: Cyclone / Alerts
    if is_there_any_storm_Bay_of_Bengal() or bay_of_bengal_alerts(API_KEY):
        rain_chance += 52

    rain_chance = min(rain_chance, 100)

    return jsonify({
        "rain": rain_chance
    })


# ---------------------------------
# Run Server
# ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)
