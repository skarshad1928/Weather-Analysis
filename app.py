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

# ✅ Enable CORS (VERY IMPORTANT)
CORS(app)

# ---------------------------------
# API Key & Location
# ---------------------------------
API_KEY = os.getenv("WEATHER_API_KEY")

LAT, LON = 32.8546, -79.9748   # Change if needed


# ---------------------------------
# Health Check Route
# ---------------------------------
@app.route("/")
def home():
    return jsonify({"status": "Weather API is running"})


# ---------------------------------
# Weather Endpoint
# ---------------------------------
@app.route("/weather", methods=["GET"])
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
# Rain Probability Endpoint
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

    # Safety cap
    rain_chance = min(rain_chance, 100)

    return jsonify({
        "rain": rain_chance
    })


# ---------------------------------
# Run Server (Render needs this)
# ---------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
