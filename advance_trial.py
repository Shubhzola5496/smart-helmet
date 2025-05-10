import streamlit as st
import requests
from urllib.parse import quote
from maps import route_details
import emailing

# --- OLA Maps API Info ---
OLA_API_KEY = "fGTkKhS1eNik9lM2Xo03Wyz4jxTwCvh1dbPYlQx8"
HEADERS = {
    "X-Request-Id": "351d63bf-20cc-4cc7-86ba-8a640c27e3d4"
}

# --- Streamlit UI ---
st.title("OLA Smart Helmet")
st.subheader("This app will support hassle-free working of your helmet")

# # --- Get suggestions from OLA Maps Autocomplete API ---
# def get_suggestions(query):
#     url = f"https://api.olamaps.io/places/v1/autocomplete?input={quote(query)}&api_key={OLA_API_KEY}"
#     try:
#         response = requests.get(url, headers=HEADERS, verify=False)
#         response.raise_for_status()
#         predictions = response.json().get("predictions", [])
#         return [item.get("description") for item in predictions]
#     except Exception as e:
#         st.error(f"Autocomplete error: {e}")
#         return []

# --- Geocode selected location ---
def geocode_address(address):
    try:
        st.write(f"🔍 Geocoding address: `{address}`")  # Optional: debug
        url = f"https://api.olamaps.io/places/v1/geocode?address={quote(address)}&api_key={OLA_API_KEY}"
        response = requests.get(url, headers=HEADERS, verify=False)
        response.raise_for_status()
        data = response.json()
        print("Geocode data",data)
        if "results" not in data or not data["results"]:
            st.warning(f"⚠️ No coordinates found for: `{address}`")
            return None

        location = data["results"][0]["geometry"]["location"]
        return f"{location['lat']},{location['lng']}"
    except Exception as e:
        st.error(f"❌ Geocoding error for `{address}`: {e}")
        return None


# # --- UI: Origin and Destination Text Input with Suggestions ---
# origin_input = st.text_input("Enter Origin Location")
# origin_suggestions = get_suggestions(origin_input) if origin_input else []
# origin_selection = st.selectbox("Select Origin", origin_suggestions) if origin_suggestions else None
#
# destination_input = st.text_input("Enter Destination Location")
# destination_suggestions = get_suggestions(destination_input) if destination_input else []
# destination_selection = st.selectbox("Select Destination", destination_suggestions) if destination_suggestions else None
#
# # --- Get Coordinates ---
# if origin_selection and destination_selection:
#     origin_coords = geocode_address(origin_selection)
#     destination_coords = geocode_address(destination_selection)
#
#     if origin_coords and destination_coords:
#         # Call your existing routing logic
#         distance, duration, instruction1, instruction2 = route_details(origin_coords, destination_coords)
#
#         # Settings
#         col1, col2 = st.columns(2)
#         with col1:
#             voice_assist = st.checkbox("Enable Voice Assistance", key="voice_assist")
#             auto_indicator = st.checkbox("Enable Auto Vehicle Indicator", key="auto_indicator")
#         with col2:
#             vehicle_control = st.checkbox("Enable Vehicle Control", key="vehicle_control")
#             connect_phone = st.checkbox("Connect to Phone", key="connect_phone")
#         volume = st.slider("Volume", 0, 100, 50)
#
#         # ESP32 Setup
#         ESP32_URL = "http://192.168.246.225:80/data"
#         status_text = st.empty()
#
#         # Function to send data
#         def send_data():
#             data = {
#                 "origin": origin_selection,
#                 "origin_coordinates": origin_coords,
#                 "destination": destination_selection,
#                 "destination_coordinates": destination_coords,
#                 "Distance": distance,
#                 "Duration": duration,
#                 "direction1": instruction1,
#                 "direction2": instruction2,
#                 "voice_assist": voice_assist,
#                 "auto_indicator": auto_indicator,
#                 "vehicle_control": vehicle_control,
#                 "connect_phone": connect_phone,
#                 "volume": volume
#             }
#             message = "\n".join([f"{k}: {v}" for k, v in data.items()])
#             try:
#                 response = requests.post(ESP32_URL, json=data, timeout=2)
#                 status_text.success(f"✅ Data Sent: {response.text}")
#             except requests.exceptions.RequestException as e:
#                 status_text.error(f"❌ Failed to send data: {e}")
#             return message
#
#         # Button to Configure
#         if st.button("Configure"):
#             email_message = send_data()
#             emailing.send_email(email_message)
#     else:
#         st.warning("Coordinates could not be determined for selected locations.")

geocode_address("bangalore")