import streamlit as st
import requests
import plotly.graph_objs as go # type: ignore
from datetime import datetime
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
print(API_KEY)
# Custom CSS for style
st.markdown("""
    <style>
    body {
        background-color: #f5f7fa;
    }
    .city-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 2px 2px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .city-title {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
    }
    hr {
        border-top: 1px solid #ccc;
    }
    </style>
""", unsafe_allow_html=True)

# City list and emojis
cities = {
    "Sydney": "🌤️",
    "Melbourne": "🌧️",
    "Brisbane": "⛅",
    "Perth": "☀️",
    "Adelaide": "🌦️",
    "Hobart": "🌨️"
}

# Fetch weather forecast data
def get_weather_data(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url)

    if res.status_code != 200:
        st.error(f"API Error {res.status_code}: {res.text}")
        return None
    data = res.json()
    forecast = {
        "datetime": [],
        "temperature": [],
        "humidity": [],
        "rain": []
    }

    for entry in data["list"]:
        forecast["datetime"].append(datetime.fromtimestamp(entry["dt"]))
        forecast["temperature"].append(entry["main"]["temp"])
        forecast["humidity"].append(entry["main"]["humidity"])
        rain = entry.get("rain", {}).get("3h", 0)
        forecast["rain"].append(rain)

    return forecast

# Main
st.title("🌏 Australian Cities Weather Forecast")
st.markdown("Compare next week's temperature 🌡️, humidity 💧, and rainfall 🌧️ for major cities.")

chart_type = st.radio("Select chart type:", ["Temperature", "Humidity", "Rainfall"], horizontal=True)

# Layout: 3 columns per row
rows = list(cities.items())
for i in range(0, len(rows), 3):
    cols = st.columns(3)
    for idx, (city, emoji) in enumerate(rows[i:i+3]):
        with cols[idx]:
            st.markdown(f"<div class='city-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='city-title'>{emoji} {city}</div>", unsafe_allow_html=True)

            data = get_weather_data(city)
            if data:
                if chart_type == "Temperature":
                    y = data["temperature"]
                    y_label = "Temperature (°C)"
                elif chart_type == "Humidity":
                    y = data["humidity"]
                    y_label = "Humidity (%)"
                else:
                    y = data["rain"]
                    y_label = "Rainfall (mm)"

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data["datetime"], y=y, mode="lines+markers", name=chart_type))
                fig.update_layout(
                    margin=dict(l=0, r=0, t=30, b=0),
                    height=300,
                    yaxis_title=y_label,
                    xaxis_title="Date/Time",
                    plot_bgcolor="#fdfdfd",
                    paper_bgcolor="#fdfdfd",
                )
                st.plotly_chart(fig, use_container_width=True, key=f"{city}_{chart_type}")
            else:
                st.error("Failed to load data.")
            st.markdown("</div>", unsafe_allow_html=True)
