import requests
import time


def send_esp32_data(payload,path):
    ESP32_IP = "192.168.24.156"  # MUST match ESP32's actual IP
    esp_port =80
    response = requests.post(
        f"http://{ESP32_IP}:{esp_port}/{path}",
        json=payload,
        timeout=10000
    )
    if response.status_code == 200:
        data = response.json()
        print("Full response data:", data)

    print(response)
    return data
    # return None

if __name__=="__main__":
    payload = {
        'voice_assist': 0,
        'rishab':1,
        'shubham':2
    }

    data = send_esp32_data(payload,"speech")
    print(data["audio_input"])