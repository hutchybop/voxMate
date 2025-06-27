import subprocess

def check_pulseaudio_devices():
    try:
        # Check for playback (speaker) devices
        result = subprocess.run(["pactl", "list", "short", "sinks"], 
                               capture_output=True, text=True)
        speakers = bool(result.stdout.strip())
        
        # Check for input (microphone) devices
        result = subprocess.run(["pactl", "list", "short", "sources"], 
                               capture_output=True, text=True)
        mics = bool(result.stdout.strip())
        
        return mics, speakers
    except FileNotFoundError:
        print("pactl not found - PulseAudio may not be installed")
        return False, False

has_mic, has_speaker = check_pulseaudio_devices()

print(f"has_mic: {has_mic}")
print(f"has_speaker: {has_speaker}")