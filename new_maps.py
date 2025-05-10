import requests
import urllib3
import streamlit as st

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = "fGTkKhS1eNik9lM2Xo03Wyz4jxTwCvh1dbPYlQx8"
HEADERS = {
    "X-Request-Id": "351d63bf-20cc-4cc7-86ba-8a640c27e3d4",
}


def route_details(origin, destination):
    try:
        # Format coordinates
        origin_str = f"{origin[0]},{origin[1]}"
        dest_str = f"{destination[0]},{destination[1]}"

        url = f"https://api.olamaps.io/routing/v1/directions?origin={origin_str}&destination={dest_str}&api_key={API_KEY}"

        response = requests.post(url, headers=HEADERS, verify=False, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Default values
        distance = "Unknown"
        duration = "Unknown"
        instructions = ["No instructions available", ""]
        print(data)
        if data.get('routes'):
            route = data['routes'][0]
            if route.get('legs'):
                leg = route['legs'][0]
                distance = leg.get('readable_distance', distance)
                duration = leg.get('readable_duration', duration)

                if leg.get('steps'):
                    steps = leg['steps']
                    instructions = [
                        steps[0].get('instructions', instructions[0]),
                        steps[1].get('instructions', instructions[1])
                    ]
                    dist_inst =[
                        steps[0].get('distance', instructions[0]),
                        steps[1].get('distance', instructions[1])
                    ]

        return distance, duration, instructions[0], instructions[1], dist_inst[0], dist_inst[1]

    except requests.exceptions.RequestException as e:
        st.error(f"Routing API error: {str(e)}")
        return "Error", "Error", "Could not get directions", ""
    except Exception as e:
        st.error(f"Routing error: {str(e)}")
        return "Error", "Error", "Could not get directions", ""