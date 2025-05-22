# #self.api_key = "uxoTDYB_nRDizByWW0t91BE-7"
import sys

import requests
import json
import os
import tempfile
import subprocess
import time
#
#
# class KrutrimTTS:
#     def __init__(self, api_key):
#         self.api_key = "uxoTDYB_nRDizByWW0t91BE-7"
#         self.base_url = "https://cloud.olakrutrim.com/api/v1/languagelabs/tts"
#         self.headers = {
#             'Content-Type': 'application/json',
#             'Authorization': f'Bearer {self.api_key}'
#         }
#
#     def generate_speech(self, text, speaker="male", language="eng"):
#         """Generate speech and return audio URL"""
#         payload = {
#             "input_text": text,
#             "input_language": language,
#             "input_speaker": speaker
#         }
#         try:
#             response = requests.post(
#                 self.base_url,
#                 headers=self.headers,
#                 data=json.dumps(payload),
#                 timeout=15
#             )
#
#             if response.status_code == 200:
#                 result = response.json()
#                 print("This is the result of generate speech",result)
#                 if result.get('status') == 'success':
#                     print(result['data']['audio_file'])
#                     return result['data']['audio_file']
#             print(f"API Error {response.status_code}: {response.text}")
#             return None
#         except Exception as e:
#             print(f"Request failed: {e}")
#             return None
#
#     def download_and_play(self, audio_url, filename="krutrim_tts_output.wav"):
#         """Download audio from URL and save to current directory, then play it"""
#         if not audio_url:
#             return False
#
#         try:
#             # Download the audio file
#             print("Downloading audio...")
#             response = requests.get(audio_url, stream=True)
#             response.raise_for_status()
#
#             # Get current script directory
#             script_dir = os.path.dirname(os.path.abspath(__file__))
#             output_path = os.path.join(script_dir, filename)
#
#             # Save to permanent location
#             with open(output_path, 'wb') as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     f.write(chunk)
#             print(f"Audio saved to: {output_path}")
#
#             # Play using system default player
#             print("Playing audio...")
#             if os.name == 'nt':  # Windows
#                 os.startfile(output_path)
#             else:  # Mac/Linux
#                 opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
#                 subprocess.run([opener, output_path])
#
#             return True
#
#         except Exception as e:
#             print(f"Playback failed: {e}")
#             return False
#
#
# if __name__ == "__main__":
#     tts = KrutrimTTS("uxoTDYB_nRDizByWW0t91BE-7")
#
#     # Test with a simple sentence
#     audio_url = tts.generate_speech("Hello, this is a test of Krutrim TTS service")
#
#     if audio_url:
#         print(f"Audio URL received: {audio_url}")
#         if tts.download_and_play(audio_url):
#             # Keep program running while audio plays
#             # input("Press Enter to exit when finished listening...")
#             pass
#         else:
#             print("Failed to play audio")
#     else:
#         print("Failed to generate audio")

class KrutrimTTS:
    def __init__(self, api_key):
        self.api_key = "uxoTDYB_nRDizByWW0t91BE-7"
        self.base_url = "https://cloud.olakrutrim.com/api/v1/languagelabs/tts"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        self.timeout = 300  # Increased timeout

    def generate_speech(self, text, speaker="female", language="eng"):
        """Generate speech with proper chunking and validation"""
        if not text or not isinstance(text, str):
            print("Error: Invalid text input")
            return None

        # Clean and validate text
        text = text.strip()
        if len(text) > 1000:  # Safe chunk size
            print("Warning: Text is long, consider chunking")

        payload = {
            "input_text": text[:1000],  # Safety limit
            "input_language": language,
            "input_speaker": speaker,
            "speed": 1.0,  # Explicit speed
            "pitch": 1.0  # Explicit pitch
        }

        try:
            print(f"Sending text: {text[:100]}...")  # Log first 100 chars
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )

            # Debug raw response
            print(f"Status: {response.status_code}")
            print(f"Headers: {response.headers}")

            result = response.json()
            print("API Response:", json.dumps(result, indent=2))

            if result.get('status') == 'success':
                audio_url = result['data']['audio_file']
                print(f"Got audio URL: {audio_url}")
                return audio_url
            else:
                print(f"API Error: {result.get('message', 'No error message')}")
                return None

        except Exception as e:
            print(f"TTS Generation Failed: {str(e)}")
            return None

    def download_and_play(self, audio_url):
        """Download with proper streaming and validation"""
        if not audio_url:
            return False

        try:
            # Create unique filename
            filename = f"tts_audio_output.wav"

            print(f"Downloading from {audio_url}...")
            with requests.get(audio_url, stream=True) as r:
                r.raise_for_status()

                # Check content length
                content_length = int(r.headers.get('content-length', 0))
                print(f"Audio size: {content_length} bytes")

                if content_length < 1024:  # If less than 1KB
                    print("Error: Audio file too small")
                    return False

                # Save file
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            # Verify file
            file_size = os.path.getsize(filename)
            print(f"Saved {file_size} bytes to {filename}")

            if file_size < 1024:
                print("Error: Saved file too small")
                return False

            # Play audio
            print("Playing audio...")
            if sys.platform == 'win32':
                os.startfile(filename)
            elif sys.platform == 'darwin':
                subprocess.run(['afplay', filename])
            else:
                subprocess.run(['aplay', filename])

            return True

        except Exception as e:
            print(f"Playback Error: {str(e)}")
            return False




if __name__ == "__main__":
    kruti = KrutrimTTS("uxoTDYB_nRDizByWW0t91BE-7")
    sound = kruti.generate_speech("Hello how are you?")
    kruti.download_and_play(sound)