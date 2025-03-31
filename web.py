import streamlit as st
import requests
import time

st.title("OLA Smart Helmet")
st.subheader("This app will support hassle-free working of your helmet")


origin = st.selectbox("Enter the origin", ("kudlu gate", "mysore", "whitefield"))
destination = st.selectbox("Enter the destination", ("ola electric technologies Pvt. Ltd. ", "kudlu gate", " kanakpura "))

col1,col2 = st.columns(2)

with col1:
    voice_assist = st.checkbox("Enable Voice Assistance", key="voice_assist")
    auto_indicator = st.checkbox("Enable Auto Vehicle Indicator", key="auto_indicator")

with col2:
    vehicle_control = st.checkbox("Enable Vehicle Control", key="vehicle_control")
    connect_phone = st.checkbox("Connect to Phone", key="connect_phone")

volume = st.slider("Volume", 0, 100, 50)

#print(voice_assist,auto_indicator,vehicle_control,connect_phone,volume)

# Flask server URL (Change to your Flask server IP)
FLASK_SERVER_URL = "http://127.0.0.1:5000/update_data"


def send_data():
    data = {
        "origin": origin,
        "destination": destination,
        "voice_assist": voice_assist,
        "auto_indicator": auto_indicator,
        "vehicle_control": vehicle_control,
        "connect_phone": connect_phone,
        "volume": volume
    }

    try:
        response = requests.post(FLASK_SERVER_URL, json=data)
        st.write("Data sent:", response.text)
    except requests.exceptions.RequestException as e:
        st.write("Error sending data:", e)


# Streamlit Loop for Real-time Updates
while True:
    send_data()
    time.sleep(1)  # Send data every 1 second
