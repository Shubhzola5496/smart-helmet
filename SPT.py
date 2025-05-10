import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
import time
import io
import json
from send_receive_data import send_esp32_data

# Configuration
SAMPLERATE = 16000  # Sample rate (Hz)
DURATION = 5 # Recording duration (seconds)
#DEVICE_INDEX = 9  # Your working mic index for bluetooth
DEVICE_INDEX =1 # For laptop mic
KRUTRIM_API_KEY = "uxoTDYB_nRDizByWW0t91BE-7"  # Replace with your actual key


def record_audio():
    """Record audio with timeout handling"""
    print(f"🎙️ Recording from device {DEVICE_INDEX} for {DURATION} seconds...")
    audio = sd.rec(int(DURATION * SAMPLERATE),
                   samplerate=SAMPLERATE,
                   channels=1,
                   dtype='int16',
                   device=DEVICE_INDEX)

    # Visual recording indicator


    for i in range(DURATION, 0, -1):
        print(f"Recording... {i}s remaining", end='\r')
        time.sleep(1)


    sd.stop()
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
        # 1. Record audio
        audio = record_audio()

        # 2. Save local copy (optional)
        wav.write("last_recording.wav", SAMPLERATE, audio)
        print("\n✅ Audio saved to 'last_recording.wav'")

        # 3. Send to Krutrim API
        print("🔄 Sending to Ola Krutrim API...")
        result = send_to_krutrim(audio, SAMPLERATE)

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
    print("starting the main function")
    SPT_main()