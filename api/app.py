from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("WEATHER_API_KEY")
LAT, LON = 32.8546, -79.9748


@app.route("/")
def home():
    return jsonify({"status": "API is running"})


@app.route("/weather")
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

    r = requests.get(url, params=params, timeout=8)
    data = r.json()

    if r.status_code != 200 or "main" not in data:
        return jsonify({"error": "Weather API failed"}), 500

    return jsonify({
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"]
    })


@app.route("/rain", methods=["POST"])
def rain():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    rain_chance = 0

    if data.get("humidity", 0) > 75:
        rain_chance += 23
    if data.get("temperature", 0) > 16:
        rain_chance += 24

    return jsonify({"rain": rain_chance})


# 🔴 THIS IS THE CRITICAL PART FOR VERCEL
def handler(environ, start_response):
    return app(environ, start_response)
