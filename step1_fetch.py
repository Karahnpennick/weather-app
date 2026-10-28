# step1_fetch.py
# STEP 1: Prove you can talk to an API from plain Python before adding any UI.
# Run with:  python step1_fetch.py

import requests   # third-party library for making web requests (pip install requests)

# ---------------------------------------------------------------------------
# Part A: Turn a city name into latitude/longitude (the "geocoding" API).
# ---------------------------------------------------------------------------

city = "Charlotte"

# The base URL of the API endpoint we want to call.
geo_url = "https://geocoding-api.open-meteo.com/v1/search"

# Query parameters. requests turns this dict into ?name=Charlotte&count=1
# so we don't have to build the URL string by hand.
geo_params = {"name": city, "count": 1}

# Send an HTTP GET request. timeout=10 stops it from hanging forever.
geo_response = requests.get(geo_url, params=geo_params, timeout=10)

# .json() converts the text the server sent back into Python dicts and lists.
geo_data = geo_response.json()

# Print the raw data so you can SEE its structure. This is how you learn
# any new API: call it, print it, look at the keys.
print("Raw geocoding response:")
print(geo_data)

# The API returns {"results": [ {...first match...} ]}.
# [0] grabs the first (best) match from the list.
place = geo_data["results"][0]
lat = place["latitude"]
lon = place["longitude"]
print(f"\n{place['name']} is at latitude {lat}, longitude {lon}")

# ---------------------------------------------------------------------------
# Part B: Use those coordinates to get the weather (the "forecast" API).
# ---------------------------------------------------------------------------

weather_url = "https://api.open-meteo.com/v1/forecast"
weather_params = {
    "latitude": lat,
    "longitude": lon,
    "current": "temperature_2m,wind_speed_10m",   # which current values we want
    "temperature_unit": "fahrenheit",
    "wind_speed_unit": "mph",
}

weather_data = requests.get(weather_url, params=weather_params, timeout=10).json()

# Dig into the nested dict to pull out just the numbers we care about.
current = weather_data["current"]
print(f"Temperature: {current['temperature_2m']} °F")
print(f"Wind speed:  {current['wind_speed_10m']} mph")
