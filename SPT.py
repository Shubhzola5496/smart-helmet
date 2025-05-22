import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
import time
import io
import json

# Configuration
DURATION = 5  # Recording duration (seconds)
KRUTRIM_API_KEY = "uxoTDYB_nRDizByWW0t91BE-7"  # Replace with your actual key


def list_audio_devices():
    """List all available audio devices and return them"""
    devices = sd.query_devices()
    print("\nAvailable Audio Input Devices:")
    input_devices = []
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"{len(input_devices)}: {dev['name']} (Channels: {dev['max_input_channels']}, "
                  f"Sample Rate: {dev['default_samplerate']}Hz)")
            input_devices.append(i)

    if not input_devices:
        ValueError("No input devices found!")
    return input_devices


def select_audio_device():
    """Let user select an audio device"""
    input_devices = list_audio_devices()

    while True:
        try:
            selection = int(input("\nSelect audio input device number: "))
            if 0 <= selection < len(input_devices):
            # selection = 4
                device_index = input_devices[selection]
                device_info = sd.query_devices(device_index)
                return device_index, int(device_info['default_samplerate'])
                print("Invalid selection! Please try again.")
        except ValueError:
                print("Please enter a valid number!")


def record_audio(device_index, sample_rate):
    """Record audio from specified device"""
    print(f"\n🎙️ Recording from device {device_index} ({sd.query_devices(device_index)['name']})")
    print(f"Sample Rate: {sample_rate}Hz, Duration: {DURATION}s")

    # Record audio
    audio = sd.rec(
        int(DURATION * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16',
        device=device_index
    )

    # Show countdown while recording
    for i in range(DURATION, 0, -1):
        print(f"Recording... {i}s remaining", end='\r')
        time.sleep(1)

    audio = np.squeeze(audio)

    if audio.size == 0:
        raise ValueError("No audio was recorded")
    return audio


def send_to_krutrim(audio_data, sample_rate):
    """Send audio to Ola Krutrim STT API"""
    url = "https://cloud.olakrutrim.com/api/v1/languagelabs/transcribe/upload"

    # Create WAV file in memory
    with io.BytesIO() as wav_buffer:
        wav.write(wav_buffer, sample_rate, audio_data)
        wav_bytes = wav_buffer.getvalue()

    files = {'file': ('recording.wav', wav_bytes, 'audio/wav')}
    payload = {'lang_code': 'eng'}  # Change language if needed
    headers = {'Authorization': f'Bearer {KRUTRIM_API_KEY}'}

    try:
        response = requests.post(url, headers=headers, data=payload, files=files)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None


def SPT_main():
    default_response = {
        'status': 'error',
        'data': {
            'text': [''],
            'language': 'en'
        }
    }

    try:
        # 1. Let user select audio device
        device_index, sample_rate = (8,44100) #select_audio_device()

        # 2. Record audio
        audio = record_audio(device_index, sample_rate)

        # 3. Save local copy (optional)
        wav.write("last_recording.wav", sample_rate, audio)
        print("\n✅ Audio saved to 'last_recording.wav'")

        # 4. Send to Krutrim API
        print("🔄 Sending to Ola Krutrim API...")
        result = send_to_krutrim(audio, sample_rate)

        if result:
            print("\n--- Transcription ---")
            print(json.dumps(result, indent=2))
            return result
        else:
            print("Failed to get transcription")
            return default_response

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return default_response


if __name__ == "__main__":
    print("Starting the main function")
    SPT_main()