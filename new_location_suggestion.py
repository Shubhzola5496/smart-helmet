import requests
from urllib.parse import quote
import streamlit as st

API_KEY = "fGTkKhS1eNik9lM2Xo03Wyz4jxTwCvh1dbPYlQx8"
HEADERS = {
    "X-Request-Id": "351d63bf-20cc-4cc7-86ba-8a640c27e3d4",
}


def get_location_suggestions(user_input):
    if not user_input.strip():
        return []

    try:
        query = quote(user_input)
        url = f"https://api.olamaps.io/places/v1/autocomplete?input={query}&api_key={API_KEY}"
        response = requests.get(url, headers=HEADERS, verify=False, timeout=5)
        response.raise_for_status()

        suggestions = response.json().get("predictions", [])
        return [place.get("description", "") for place in suggestions if place.get("description")]

    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Error processing suggestions: {str(e)}")
        return []


def geo_loc(address):
    if not address.strip():
        return None, None

    try:
        params = {
            "address": address,
            "language": "en",
            "api_key": API_KEY
        }
        response = requests.get(
            "https://api.olamaps.io/places/v1/geocode",
            headers=HEADERS,
            params=params,
            verify=False,
            timeout=5
        )
        response.raise_for_status()

        data = response.json()
        if data.get("geocodingResults"):
            first_result = data["geocodingResults"][0]
            return (
                first_result["geometry"]["location"]["lat"],
                first_result["geometry"]["location"]["lng"]
            )
        return None, None

    except requests.exceptions.RequestException as e:
        st.error(f"Geocoding network error: {str(e)}")