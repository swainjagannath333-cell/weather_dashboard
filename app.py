import streamlit as st
import requests
import pandas as pd

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Weather Dashboard", layout="wide")

# ---- TITLE ----
st.title("🌦️ Weather Dashboard")
st.caption("Simple weather insights for any city")

# ---- INPUT ----
city = st.text_input("Enter city name")

if city:
    # ---- STEP 1: GET LOCATION (Geocoding) ----
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    geo_response = requests.get(geo_url)

    if geo_response.status_code == 200:
        geo_data = geo_response.json()

        if "results" in geo_data:
            options = geo_data["results"]

            city_options = [
                f"{loc['name']}, {loc['country']}" for loc in options
            ]

            selected = st.selectbox("Select location", city_options)

            selected_index = city_options.index(selected)
            location = options[selected_index]

            lat = location["latitude"]
            lon = location["longitude"]

            st.success(f"📍 Selected: {selected}")

            # ---- STEP 2: GET WEATHER ----
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,windspeed_10m&daily=temperature_2m_max,precipitation_sum"

            response = requests.get(weather_url)

            if response.status_code == 200:
                data = response.json()

                # ---- DATAFRAME ----
                df = pd.DataFrame({
                    "time": data["hourly"]["time"],
                    "temperature": data["hourly"]["temperature_2m"],
                    "windspeed": data["hourly"]["windspeed_10m"]
                })

                df["time"] = pd.to_datetime(df["time"])
                df = df.head(24)

                # ---- METRICS ----
                st.subheader("📊 Key Insights")

                col1, col2, col3 = st.columns(3)

                col1.metric("🌡️ Avg Temp", f"{round(df['temperature'].mean(), 1)} °C")
                col2.metric("🔥 Max Temp", f"{df['temperature'].max()} °C")
                col3.metric("❄️ Min Temp", f"{df['temperature'].min()} °C")

                # ---- RAIN CHECK ----
                rain_today = data["daily"]["precipitation_sum"][0]

                if rain_today > 0:
                    st.info("🌧️ Rain expected today")
                else:
                    st.info("☀️ No rain today")

                # ---- GRAPH ----
                st.subheader("📈 Temperature Trend (Next 24h)")
                st.line_chart(df.set_index("time")["temperature"])

                # ---- TABLE ----
                with st.expander("📋 View Raw Data"):
                    st.dataframe(df)

                # ---- MAP ----
                st.subheader("📍 Location Map")

                map_df = pd.DataFrame({
                    "lat": [lat],
                    "lon": [lon]
                })

                st.map(map_df)

            else:
                st.error("Failed to fetch weather data")

        else:
            st.error("City not found")

    else:
        st.error("Location API error")