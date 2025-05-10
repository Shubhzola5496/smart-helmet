import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import time

samplerate = 16000
duration = 5  # seconds
index = 9 # Start with WASAPI (index=17)

try:
    print(f"🎙️ Testing device {index}: {sd.query_devices(index)['name']}")
    print(f"Recording for {duration} seconds...")

    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16', device=index)

    # Force-stop after 5 seconds (if wait() hangs)
    time.sleep(duration)
    sd.stop()

    audio = np.squeeze(audio)
    if audio.size == 0:
        raise ValueError("No audio recorded!")

    filename = f"bluetooth_test_{index}.wav"
    wav.write(filename, samplerate, audio)
    print(f"✅ Saved as {filename}")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Try another index or check Bluetooth connection.")