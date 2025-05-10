import requests
import urllib3
import streamlit as st
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set your API key here
api_key = "fGTkKhS1eNik9lM2Xo03Wyz4jxTwCvh1dbPYlQx8"


# Headers
headers = {
    "X-Request-Id": "351d63bf-20cc-4cc7-86ba-8a640c27e3d4",
}

def route_details(origin,destination):
    # Build the URL
    url = f"https://api.olamaps.io/routing/v1/directions?origin={origin}&destination={destination}&api_key={api_key}"

    # Make the POST request
    response = requests.post(url, headers=headers, verify=False)

    # Parse the JSON response
    data = response.json()

    # Extracting relevant details
    if response.status_code == 200 and 'routes' in data:
        route = data['routes'][0]  # Assuming there is one route in the response
        if 'legs' in route:
            leg = route['legs'][0]  # Assuming there is one leg in the response
            total_distance = leg["readable_distance"]
            total_duration = leg['duration']  # Total duration in seconds from 'legs'
            readable_duration = leg['readable_duration']  # Human-readable format

            # Extracting instructions for each step
            steps = leg['steps']
            instructions_list = [step['instructions'] for step in steps]

            # Output the results
            print(f"Total duration to reach destination: {readable_duration}")
            print(f"Time in seconds: {total_duration} seconds")
            print(f"Total distance: {total_distance} km")
            print("\nInstructions for the route:")

            for index, instruction in enumerate(instructions_list, 1):
                print(f"Step {index}: {instruction}")
            return total_distance,readable_duration,instructions_list[0],instructions_list[1]
        else:
            print("Error: No legs found in the route.")
    else:
        print("Error: Unable to fetch data. Status code:", response.status_code)

