import streamlit as st
import requests
import urllib3
from maps import route_details
import emailing

st.title("OLA Smart Helmet KAVACH")
st.subheader("This app will support hassle-free working of your helmet")

OLA_API_KEY ="fGTkKhS1eNik9lM2Xo03Wyz4jxTwCvh1dbPYlQx8"
origin = st.selectbox("Enter the origin", ("kudlu gate", "mysore", "whitefield"))
destination = st.selectbox("Enter the destination", ( "kudlu gate",  "mysore", "whitefield"))

def location_coord(origin,destination):
    match origin:
        case "kudlu gate":
            origin = "12.8910, 77.6400"
        case "mysore":
            origin ="12.2958, 76.6394"
        case "whitefield":
            origin = "12.9698, 77.7500"
    match destination:
        case "kudlu gate":
            destination = "12.8910, 77.6400"
        case "mysore":
            destination = "12.2958, 76.6394"
        case "whitefield":
            destination = "12.9698, 77.7500"
    return origin,destination

new_ori,new_dest = location_coord(origin,destination)


print("origin:", new_ori)
print("dest:", new_dest)
distance,duration,instruction1,instruction2 = route_details(new_ori,new_dest)

instructions =[instruction1,instruction2]
print("Instruction1" , instruction1)
print('Instruction2', instruction2)


def map_id(x):
        #0 : Not activated
        #1 : left
        #2 :  right
        #3 :  straight
        #4 : uturn
        #5 : slight right
        #6 : slight left
    if "Not connected" in x:
        x=0
    elif "left" in x:
        x=1
    elif "right" in x:
        x=2
    elif ("west" or "north" or "south" or "east"or"straight") in x:
        x=3
    elif "uturn" in x:
        x=4
    elif "slight right" in x:
        x=5
    elif "slight left" in x:
        x=6
    return x

in1 = map_id(instruction1)
in2 = map_id(instruction2)

print("Bit map values for directions1",in1)
print("Bit map values for directions2",in2)
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
ESP32_URL = "http://192.168.246.225:80/data"  # Update with actual ESP32 IP

status_text = st.empty()  # Placeholder for status updates


# Function to Send Data to ESP32
def send_data():
    data = {
        "origin" : origin,
        "origin_coordinates" :new_ori,
        "destination_coordinates" :new_dest,
        "destination" : destination,
        "Distance" : distance,
        "Duration" : duration,
        "direction1" : instruction1,
        "direction2": instruction2,
        "voice_assist": voice_assist,
        "auto_indicator": auto_indicator,
        "vehicle_control": vehicle_control,
        "connect_phone": connect_phone,
        "volume": volume
    }
    message = "\n".join([f"{key}: {value}" for key, value in data.items()])
    try:
        response = requests.post(ESP32_URL, json=data, timeout=2)
        status_text.write(f"✅ Data Sent: {response.text}")
    except requests.exceptions.RequestException as e:
        status_text.write(f"❌ Error sending data: {e}")
    return message


if st.button("Configure"):
    email_message = send_data()  # send formated data to ESP controller
    emailing.send_email(email_message)  # Send email
    print()