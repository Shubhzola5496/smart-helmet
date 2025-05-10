
import requests
from urllib.parse import quote

# OLA Maps API details
API_KEY = "fGTkKhS1eNik9lM2Xo03Wyz4jxTwCvh1dbPYlQx8"
HEADERS = {
    "X-Request-Id": "351d63bf-20cc-4cc7-86ba-8a640c27e3d4",
}

def get_location_suggestions(user_input):
    if not user_input:
        return []
    query = quote(user_input)
    url = f"https://api.olamaps.io/places/v1/autocomplete?input={query}&api_key={API_KEY}"
    try:
        response = requests.get(url, headers=HEADERS, verify=False)
        response.raise_for_status()
        suggestions = response.json().get("predictions", [])
        return [place.get("description", "") for place in suggestions]
    except Exception as e:
        print(f"Error fetching suggestions: {e}")
        return []

def geo_loc(address):
    if not address:
        return None, None
    params = {
        "address": f"{address}",
        "language": "en",
        "api_key": API_KEY
    }
    response = requests.get("https://api.olamaps.io/places/v1/geocode", headers=HEADERS, params=params, verify=False)
    if response.status_code == 200:
        data = response.json()
        if data.get("geocodingResults"):
            first_result = data["geocodingResults"][0]
            lat = first_result["geometry"]["location"]["lat"]
            lng = first_result["geometry"]["location"]["lng"]
            return lat, lng
    return None, None


















# import streamlit as st
# import requests
# from urllib.parse import quote
#
# # OLA Maps API details
# API_KEY = "fGTkKhS1eNik9lM2Xo03Wyz4jxTwCvh1dbPYlQx8"
# HEADERS = {
#     "X-Request-Id": "351d63bf-20cc-4cc7-86ba-8a640c27e3d4",
# }
#
# def get_location_suggestions(user_input):
#     if not user_input:
#         return []
#     query = quote(user_input)
#     url = f"https://api.olamaps.io/places/v1/autocomplete?input={query}&api_key={API_KEY}"
#     try:
#         response = requests.get(url, headers=HEADERS, verify=False)
#         response.raise_for_status()
#         suggestions = response.json().get("predictions", [])
#         return [place.get("description", "") for place in suggestions]
#     except Exception as e:
#         st.error(f"Error fetching suggestions: {e}")
#         return []
#
#
#
# def geo_loc(address):
#     params = {
#              "address": f"{address}",
#              "language": "en",
#              "api_key": API_KEY
#               }
#     response = requests.get("https://api.olamaps.io/places/v1/geocode", headers=HEADERS, params=params, verify=False)
#     if response.status_code == 200:
#         data = response.json()
#         #print("✅ Response:", data)
#     else:
#         print("❌ Error:", response.status_code, response.text)
#
#     # Extract coordinates of the first result
#     if data.get("geocodingResults"):
#         first_result = data["geocodingResults"][0]
#         lat = first_result["geometry"]["location"]["lat"]
#         lng = first_result["geometry"]["location"]["lng"]
#         #print(f"Latitude: {lat}, Longitude: {lng}")
#     else:
#         print("No results found.")
#     return lat,lng
#
#
# #Streamlit App
# st.title("Smart Helmet HUD - Location Auto-Suggestion")
#
# # Input text
# user_input = st.text_input("Enter a place:")
#
# # Only call API when user types something
# if user_input:
#     suggestions = get_location_suggestions(user_input)
#
#     if suggestions:
#         selected_place = st.selectbox("Did you mean:", suggestions)
#         st.success(f"You selected: {selected_place}")
#     else:
#         st.write([])
#
# coord_lat,coord_lon = geo_loc(selected_place)
#
# print(coord_lat,coord_lon)