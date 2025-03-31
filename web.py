import streamlit as st
import requests
import time



import emailing

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

## ESP32 Server URL (Change to your ESP32 local network IP)
ESP32_URL = "http://192.168.1.100/update"  # Update with actual ESP32 IP

status_text = st.empty()  # Placeholder for status updates

# Function to Send Data to ESP32
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
        response = requests.post(ESP32_URL, json=data, timeout=2)
        status_text.write(f"✅ Data Sent: {response.text}")
    except requests.exceptions.RequestException as e:
        status_text.write(f"❌ Error sending data: {e}")

# Background Loop to Send Data Every 1 Second
while True:
    send_data()
    time.sleep(1)  # Send data every 1 second
    emailing.send("smart helmet data sent successfully")

if __name__== "__main__":
    emailing.send("smart helmet data sent successfully")