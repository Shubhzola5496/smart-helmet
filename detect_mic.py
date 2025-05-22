import sounddevice as sd
import numpy as np
import time


def list_audio_devices():
    """List all available audio devices"""
    devices = sd.query_devices()
    print("\nAvailable audio devices:")
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']} (Input Channels: {device['max_input_channels']}, "
              f"Output Channels: {device['max_output_channels']})")
    return devices


def test_input_device(device_index, duration=3):
    """Test an input device by recording audio"""
    device = sd.query_devices(device_index)
    if device['max_input_channels'] == 0:
        print(f"Device {device_index} has no input channels!")
        return

    print(f"\nTesting input device {device_index}: {device['name']}")
    print("Speak into your microphone...")

    fs = 44100  # Sample rate
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=device_index)
    sd.wait()  # Wait until recording is finished

    # Calculate volume level
    volume = np.sqrt(np.mean(recording ** 2))
    if volume > 0.01:  # Arbitrary threshold
        print(f"Success! Audio detected on device {device_index} (volume level: {volume:.2f})")
    else:
        print(f"No audio detected on device {device_index}. Check your microphone.")


def test_output_device(device_index, duration=2):
    """Test an output device by playing a test tone"""
    device = sd.query_devices(device_index)
    if device['max_output_channels'] == 0:
        print(f"Device {device_index} has no output channels!")
        return

    print(f"\nTesting output device {device_index}: {device['name']}")
    print("You should hear a test tone...")

    fs = 44100  # Sample rate
    t = np.linspace(0, duration, int(fs * duration), False)
    tone = np.sin(2 * np.pi * 440 * t) * 0.2  # 440 Hz sine wave

    try:
        sd.play(tone, samplerate=fs, device=device_index)
        sd.wait()
        print(f"Test tone played on device {device_index}")
    except Exception as e:
        print(f"Error playing audio on device {device_index}: {str(e)}")


def main():
    print("Bluetooth Audio Port Verification Tool")
    print("-------------------------------------")

    devices = list_audio_devices()

    while True:
        print("\nOptions:")
        print("1. Test an input device (microphone)")
        print("2. Test an output device (speaker)")
        print("3. List all devices again")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            try:
                index = int(input("Enter device index to test as input: "))
                test_input_device(index)
            except (ValueError, IndexError):
                print("Invalid device index!")
        elif choice == '2':
            try:
                index = int(input("Enter device index to test as output: "))
                test_output_device(index)
            except (ValueError, IndexError):
                print("Invalid device index!")
        elif choice == '3':
            devices = list_audio_devices()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")

