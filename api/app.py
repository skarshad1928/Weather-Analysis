from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

# ---------------------------------
# Environment variable
# ---------------------------------
API_KEY = os.getenv("WEATHER_API_KEY")

# Example location (change if needed)
LAT, LON = 32.8546, -79.9748


# ---------------------------------
# Cyclone Detection – Bay of Bengal
# ---------------------------------
def is_there_any_storm_Bay_of_Bengal():
    url = "https://dev.tropicalinfo.com/api/storms"
    try:
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            return False

        storms = r.json()
        for storm in storms:
            lat = storm.get("lat")
            lon = storm.get("lon")

            if lat is not None and lon is not None:
                if 5 <= lat <= 22 and 80 <= lon <= 100:
                    return True
        return False

    except Exception:
        return False


# ---------------------------------
# Weather Endpoint
# ---------------------------------
@app.route("/weather", methods=["GET"])
def weather():
    if not API_KEY:
        return jsonify({"error": "WEATHER_API_KEY missing"}), 500

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": LAT,
        "lon": LON,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        r = requests.get(url, params=params, timeout=8)
        data = r.json()

        if r.status_code != 200 or "main" not in data:
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

    # Rule-based logic
    if humidity > 75:
        rain_chance += 23

    if temperature > 16:
        rain_chance += 24

    if is_there_any_storm_Bay_of_Bengal():
        rain_chance += 52

    return jsonify({
        "rain": min(rain_chance, 100)
    })


# ---------------------------------
# Vercel entry point (DO NOT REMOVE)
# ---------------------------------
def handler(request, context):
    return app(request, context)
