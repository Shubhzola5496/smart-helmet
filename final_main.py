import streamlit as st
import requests
from location_suggestions import get_location_suggestions, geo_loc
from new_maps import route_details
import urllib3
from urllib.parse import quote
from TTS import KrutrimTTS
from SPT import SPT_main
from text_generation import prompt_response
import time
import os
from send_receive_data import send_esp32_data
from text_generation import process_input

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# App Configuration
st.set_page_config(
    page_title="OLA Smart Helmet KAVACH",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
<style>
    .header-style {
        font-size: 20px;
        font-weight: bold;
        color: #4a4a4a;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .section {
        padding: 15px;
        border-radius: 10px;
        background-color: white;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

#TTS







# Initialize session state
if 'route_data' not in st.session_state:
    st.session_state.route_data = None

# App Header
st.title("OLA Smart Helmet KAVACH")
st.markdown("""
<div style="background-color:#f0f2f6;padding:10px;border-radius:10px;margin-bottom:20px">
    <h3 style="color:#333;text-align:center;">Your Intelligent Riding Companion</h3>
</div>
""", unsafe_allow_html=True)

# =============================================
# ALWAYS VISIBLE SECTION (Shows immediately)
# =============================================

with st.container():
    st.header("⚙️ Helmet Configuration")

    col1, col2 = st.columns(2)
    with col1:
        voice_assist = st.toggle("Voice Guidance", True, key="voice_toggle")
        auto_indicator = st.toggle("Auto Turn Signals", True, key="indicator_toggle")
        vehicle_control = st.toggle("Vehicle controls", True,key="vehicle_control")

    with col2:
        hazard_light = st.toggle("Auto Hazard Lights", False, key="hazard_toggle")
        phone_connect = st.toggle("Phone Connectivity", True, key="phone_toggle")



    audio_speed = st.slider("audio speed", 0, 10, 5, key="audio_speed_slider")
    audio_tone = st.slider("audio tone", 0, 10, 5, key="audio_tone_slider")
    volume = st.slider("Volume Level", 0, 10, 5, key="volume_slider")

    # ESP32 Configuration
    with st.expander("Advanced Settings", expanded=False):
        esp_ip = st.text_input("ESP32 IP Address", "192.168.4.1", key="esp_ip")
        esp_port = st.text_input("Port", "80", key="esp_port")

    animation_selection = ["Wipe left to right","Wipe Right to Left","Blink All"," Bounce (Knight Rider)"," Moving Dot","Breathing"]

    selected_animation =  st.selectbox("Select an animation:",animation_selection)

def animation_bit(x):
    match x:
        case "Wipe left to right":
            x=1
        case "Wipe Right to Left":
            x=2
        case "Blink All":
            x=3
        case "Bounce (Knight Rider)":
            x=4
        case " Moving Dot":
            x=5
        case "Breathing":
            x=6
    return x

# =============================================
# ROUTE PLANNING SECTION (Conditional)
# =============================================

with st.container():
    st.header("📍 Route Planning")
    col1, col2 = st.columns(2)
    with col1:
        origin_input = st.text_input("Enter starting point:", key="origin")
    with col2:
        dest_input = st.text_input("Enter destination:", key="destination")


# Location Suggestions
def get_suggestions(input_text, key):
    if input_text:
        try:
            suggestions = get_location_suggestions(input_text)
            if suggestions:
                return st.selectbox(
                    f"Select from suggestions for {key}:",
                    suggestions,
                    key=f"suggest_{key}"
                )
        except Exception as e:
            st.error(f"Error getting suggestions: {str(e)}")
    return None


selected_origin = get_suggestions(origin_input, "origin")
selected_dest = get_suggestions(dest_input, "destination")

# Route Processing
if selected_origin and selected_dest:
    with st.spinner("Calculating your route..."):
        try:
            origin_coords = geo_loc(selected_origin)
            dest_coords = geo_loc(selected_dest)

            if None in origin_coords or None in dest_coords:
                st.error("Could not get coordinates for the locations.")
            else:
                distance, duration, instr1, instr2,inst1_dist,inst2_dist = route_details(origin_coords, dest_coords)
                st.session_state.route_data = {
                    'distance': str(distance),
                    'duration': str(duration),
                    'instructions': [instr1, instr2],
                    'coords': {
                        'origin': origin_coords,
                        'destination': dest_coords
                    },
                    'Instruction_dist' : [inst1_dist,inst2_dist]
                }
                new_inst2 = f"{instr2}  {str(inst2_dist)} m"
                print("This is the updated distance for inst 2 you wanted", instr2+" "+str(inst2_dist)+"m")
                # Display Route Info
                st.success("Route calculated successfully!")
                with st.expander("View Route Details", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("Distance", distance)
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("Duration", duration)
                        st.markdown('</div>', unsafe_allow_html=True)

                    st.subheader("Key Directions")
                    for i, instr in enumerate([instr1, instr2], 1):
                        st.write(f"{i}. {instr}")

        except Exception as e:
            st.error(f"Route calculation failed: {str(e)}")

# =============================================
# SEND TO HELMET SECTION (Always visible)
# =============================================

with st.container():
    st.header("📲 Helmet Communication")

    if st.button("Send Configuration to Helmet", type="primary", key="send_button"):
        try:
            # Prepare payload with current settings
            def map_id(instr):
                if "left" in instr:
                    return 1 if "slight" not in instr else 6
                elif "right" in instr:
                    return 2 if "slight" not in instr else 5
                elif "straight" in instr or any(d in instr for d in ["north", "south", "east", "west"]):
                    return 3
                elif "uturn" in instr:
                    return 4
                return 0

            print(map_id(instr2))
            payload = {
                'voice_assist': 1 if voice_assist else 0,
                'auto_indicator': 1 if auto_indicator else 0,
                'hazard_light': 1 if hazard_light else 0,
                'connect_phone': 1 if phone_connect else 0,
                'vehicle_control' : 1 if vehicle_control else 0,
                'volume': volume,
                "direction1_bit": map_id(instr1),
                "direction2_bit": map_id(instr2),
                "origin": origin_input,
                "destination": dest_input,
                "duration": duration,
                "distance": distance,
                "instruction_dist1":inst1_dist,
                "instruction_dist2":new_inst2, #total instruction
                "animation" : animation_bit(selected_animation),
                "audio_speed": audio_speed,
                "audio_tone": audio_tone
            }
            print(payload)
            # Add route data if available
            if st.session_state.route_data:
                def map_instr(instr):
                    instr = instr.lower()
                    if "left" in instr:
                        return 1 if "slight" not in instr else 6
                    elif "right" in instr:
                        return 2 if "slight" not in instr else 5
                    elif "straight" in instr or any(d in instr for d in ["north", "south", "east", "west"]):
                        return 3
                    elif "uturn" in instr:
                        return 4
                    return 0


                payload['instructions'] = [
                    map_instr(instr) for instr in st.session_state.route_data['instructions']
                ]
                payload['coords'] = st.session_state.route_data['coords']

            with st.spinner("Connecting to helmet..."):
                response = send_esp32_data(payload,path="")
                if response.status_code == 200:
                    st.success("Helmet configured successfully!")
                else:
                    st.error(f"Helmet connection failed (Status: {response.status_code})")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")

# With this safer version:
def continuous_SPT(busy_flag):
    if busy_flag==0:
        status_flag=0
        SPT_data = SPT_main()
        busy_flag = 1
        payload_flag = {
            "busy_flag": busy_flag
        }
        try:
            transcribed_data = SPT_data.get('data', {}).get('text', [''])[0]

            print(f"Transcribed: {transcribed_data}")

            print("this is the frist instance of busy flag",busy_flag)
        except (AttributeError, IndexError) as e:
            print(f"Error processing transcription: {e}")
            transcribed_data = ""

        vehicle_commands = process_input(transcribed_data)
        if vehicle_commands == "None":

            send_esp32_data(payload_flag,"flag")
            prompt_data = str(prompt_response(transcribed_data))
            print("This is prompt data",prompt_data)
            print(type(prompt_data))


            #TTS
            tts = KrutrimTTS("uxoTDYB_nRDizByWW0t91BE-7")

            send_esp32_data(payload_flag, "flag")
            print("this is the second instance of busy flag", busy_flag)

            # Generate speech from prompt_data
            audio_url = tts.generate_speech(
                text=prompt_data,
                speaker="male"  # Explicitly set voice
            )

            if audio_url:
                print(f"Audio URL received: {audio_url}")

                if not tts.download_and_play(audio_url):
                    status_flag = 1
                    payload_flag = {
                        "status_flag": status_flag
                    }
                    print(status_flag)
                    send_esp32_data(payload_flag, "flag")
                    print("Failed to play audio")
            else:
                print("Failed to generate audio")
                status_flag = 1
                payload_flag = {
                    "status_flag": status_flag
                }
                print(status_flag)
                send_esp32_data(payload_flag, "flag")

                send_esp32_data(payload_flag, "flag")
                prompt_data = str(prompt_response(transcribed_data))
                print("This is prompt data", prompt_data)
                print(type(prompt_data))

                # TTS
                tts = KrutrimTTS("uxoTDYB_nRDizByWW0t91BE-7")

                send_esp32_data(payload_flag, "flag")
                print("this is the second instance of busy flag", busy_flag)

                # Generate speech from prompt_data
                audio_url = tts.generate_speech(
                    text=prompt_data,
                    speaker="male"  # Explicitly set voice
                )

                if audio_url:
                    print(f"Audio URL received: {audio_url}")

                    if not tts.download_and_play(audio_url):
                        status_flag = 1
                        payload_flag = {
                            "status_flag": status_flag
                        }
                        print(status_flag)
                        send_esp32_data(payload_flag, "flag")
                        print("Failed to play audio")

            busy_flag = 0
            print("Busy flag after running the audio:",busy_flag)
            return busy_flag
        else:
            payload_command = {
                "vehicle_command":vehicle_commands
            }
            send_esp32_data(payload_command,path="")

while True:
    time.sleep(5)
    # payload_2 = {
    #     "busy_flag" : 0,
    #     "status_flag" :0
    # }
    # data = send_esp32_data(payload_2,path="speech")
    # if data["audio_input"]==1:
    #     busy_flag_val = 0
    #     busy_flag_val = continuous_SPT(busy_flag_val)
    #     payload_2["busy_flag"] = busy_flag_val

    #laptop check
    continuous_SPT(0)




# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#666;font-size:14px;">
    OLA Smart Helmet KAVACH | Safe Riding Technology
</div>
""", unsafe_allow_html=True)