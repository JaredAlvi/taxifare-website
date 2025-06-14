import streamlit as st
import requests
from datetime import datetime, time
import pandas as pd
import math

st.set_page_config(page_title="NYC Taxi Fare", layout="centered")

st.title("NYC Taxi Fare Predictor")
st.markdown(
    'Ajusta los parámetros en la barra lateral para obtener la tarifa estimada.'
)

with st.sidebar:
    st.header("Ride parameters")

    # Fecha y hora
    pickup_date = st.date_input("Pickup date", value=datetime.now().date())
    pickup_time = st.time_input("Pickup time", value=time(12, 0))

    # Coordenadas (sliders dentro del rango aproximado de NYC)
    pickup_longitude = st.slider(
        "Pickup longitude", min_value=-74.3, max_value=-73.7,
        value=-73.985428, step=0.0001, format="%.6f"
    )
    pickup_latitude = st.slider(
        "Pickup latitude", min_value=40.5, max_value=40.9,
        value=40.758896, step=0.0001, format="%.6f"
    )
    dropoff_longitude = st.slider(
        "Drop-off longitude", min_value=-74.3, max_value=-73.7,
        value=-73.985428, step=0.0001, format="%.6f"
    )
    dropoff_latitude = st.slider(
        "Drop-off latitude", min_value=40.5, max_value=40.9,
        value=40.748817, step=0.0001, format="%.6f"
    )

    # Pasajeros
    passenger_count = st.slider("Passengers", min_value=1, max_value=8, value=1)

    # Botón
    predict_btn = st.button("Consultar")

API_URL = "https://taxifare.lewagon.ai/predict"

if predict_btn:
    pickup_datetime = datetime.combine(pickup_date, pickup_time).strftime("%Y-%m-%d %H:%M:%S")

    params = {
        "pickup_datetime": pickup_datetime,
        "pickup_longitude": pickup_longitude,
        "pickup_latitude": pickup_latitude,
        "dropoff_longitude": dropoff_longitude,
        "dropoff_latitude": dropoff_latitude,
        "passenger_count": passenger_count
    }

    with st.spinner("Consultando modelo…"):
        try:
            response = requests.get(API_URL, params=params, timeout=10)
            response.raise_for_status()
            fare = response.json().get("fare", None)
        except Exception as e:
            st.error(f"Error al llamar la API: {e}")
            st.stop()

    st.success(f"Tarifa estimada: **${fare:.2f}** USD")

    # Distancia aproximada
    def distancia(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    dist_km = distancia(pickup_latitude, pickup_longitude, dropoff_latitude, dropoff_longitude)
    st.metric("Distancia del viaje", f"{dist_km:.2f} km")

    # Mapa con ubicaciones
    df_map = pd.DataFrame({
        "lat": [pickup_latitude, dropoff_latitude],
        "lon": [pickup_longitude, dropoff_longitude]
    })
    st.map(df_map, zoom=11)
