from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# ---------------------------------
# Load environment variables
# ---------------------------------
load_dotenv()

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("WEATHER_API_KEY")

# Charleston, South Carolina (North Atlantic coast)
LAT, LON = 32.8546, -79.9748

# ---------------------------------
# Cyclone flag (MANUAL / ASSUMED)
# ---------------------------------
def is_cyclone_in_north_atlantic():
    """
    NOTE:
    There is no free API to detect nearest cyclone.
    This flag represents cyclone presence in North Atlantic.
    In real systems this comes from NOAA/NHC.
    """
    return True   # 🔁 change to False if no cyclone

# ---------------------------------
# Health check
# ---------------------------------
@app.route("/")
def home():
    return jsonify({"status": "Weather API is running"})

# ---------------------------------
# Weather API
# ---------------------------------
@app.route("/weather")
def weather():
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": LAT,
        "lon": LON,
        "appid": API_KEY,
        "units": "metric"
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    return jsonify({
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_direction": data["wind"].get("deg", 0)
    })

# ---------------------------------
# Rain Probability Logic (YOUR RULES)
# ---------------------------------
@app.route("/rain", methods=["POST"])
def rain():
    data = request.get_json()

    temp = data.get("temperature")
    humidity = data.get("humidity")
    wind_deg = data.get("wind_direction")

    rain_chance = 0

    # 1️⃣ Temperature rule
    if temp > 16:
        rain_chance += 25

    # 2️⃣ Humidity rule
    if humidity > 75:
        rain_chance += 25

    # 3️⃣ Wind from South (135°–225°)
    if 135 <= wind_deg <= 225:
        rain_chance += 8

    # 4️⃣ Cyclone in North Atlantic
    if is_cyclone_in_north_atlantic():
        rain_chance += 20

    return jsonify({
        "rain_probability": rain_chance,
        "logic": {
            "temperature_rule": temp > 16,
            "humidity_rule": humidity > 75,
            "south_wind_rule": 135 <= wind_deg <= 225,
            "cyclone_present": is_cyclone_in_north_atlantic()
        }
    })

# ---------------------------------
# Run server
# ---------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
