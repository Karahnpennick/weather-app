# app.py
# STEP 2: Turn the API code into a web app with Streamlit.
# Run with:  streamlit run app.py
# A browser tab opens automatically at http://localhost:8501

import requests            # makes the API calls
import pandas as pd        # holds table data for the chart (installed with Streamlit)
import streamlit as st     # turns this Python script into a web page

# ---------------------------------------------------------------------------
# Helper functions: each one does ONE job. Small functions are easy to test
# and easy for teammates to work on separately.
# ---------------------------------------------------------------------------

def get_coordinates(city):
    """Look up a city name and return (name, region, lat, lon), or None if not found."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    data = requests.get(url, params={"name": city, "count": 1}, timeout=10).json()

    # If the city doesn't exist, the API leaves out "results" entirely.
    # .get() returns None instead of crashing with a KeyError.
    results = data.get("results")
    if not results:
        return None

    place = results[0]
    # admin1 is the state/province. Not every place has one, so use .get() with a default.
    return place["name"], place.get("admin1", ""), place["latitude"], place["longitude"]


def get_weather(lat, lon):
    """Fetch current conditions plus a 7-day high/low forecast for a location."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,relative_humidity_2m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "timezone": "auto",   # dates come back in the city's local time zone
    }
    return requests.get(url, params=params, timeout=10).json()


# ---------------------------------------------------------------------------
# The page itself. Streamlit runs this whole file top to bottom every time
# the user interacts with something, and draws each st.* call in order.
# ---------------------------------------------------------------------------

st.title("Quick Weather")
st.write("Type a city to see current conditions and the week ahead.")

# A text box. Whatever the user types is stored in the variable `city`.
city = st.text_input("City", value="Charlotte")

# st.button returns True only on the run right after it's clicked.
if st.button("Get weather"):

    # try/except keeps the app from crashing if the internet or API fails.
    try:
        # Show a spinner while we wait on the network.
        with st.spinner("Fetching data..."):
            location = get_coordinates(city)

            if location is None:
                # st.error shows a red message box.
                st.error(f"Couldn't find a city called '{city}'. Check the spelling.")
                st.stop()   # end this run here so nothing below executes

            # "Unpack" the tuple into four separate variables.
            name, region, lat, lon = location
            weather = get_weather(lat, lon)

        st.subheader(f"{name}, {region}" if region else name)

        # --- Current conditions shown as three side-by-side cards ---
        current = weather["current"]
        col1, col2, col3 = st.columns(3)   # split the row into 3 equal columns
        col1.metric("Temperature", f"{current['temperature_2m']:.0f} °F")  # :.0f = no decimals
        col2.metric("Wind", f"{current['wind_speed_10m']:.0f} mph")
        col3.metric("Humidity", f"{current['relative_humidity_2m']}%")

        # --- 7-day forecast as a line chart ---
        daily = weather["daily"]
        # Build a table: one row per day, with columns for high and low.
        forecast = pd.DataFrame({
            "High (°F)": daily["temperature_2m_max"],
            "Low (°F)": daily["temperature_2m_min"],
        }, index=pd.to_datetime(daily["time"]))   # dates become the x-axis

        st.subheader("7-day forecast")
        st.line_chart(forecast)

        # The same data as a table, in case someone wants exact numbers.
        st.dataframe(forecast)

    except requests.RequestException:
        # Catches network problems: no internet, timeouts, API down.
        st.error("Couldn't reach the weather service. Check your connection and try again.")
