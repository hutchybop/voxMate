import subprocess

def check_pulseaudio_devices():
    try:
        # Check for playback (speaker) devices
        result = subprocess.run(["pactl", "list", "short", "sinks"], 
                               capture_output=True, text=True)
        speakers = bool(result.stdout.strip())
        if not speakers:
            print(""" 
                ❌ Speaker not detected!
                Troubleshoot speaker:
                    • No speaker detected. RPi-specific checks:
                    • 1. Ensure speaker is connected properly
                    • 2. Check ALSA: aplay -l
                    • 3. Set default sink: pacmd set-default-sink <name>
                    • 4. Check volume: amixer -D pulse sset Master 100% unmute
            """)
        
        # Check for input (microphone) devices
        result = subprocess.run(["pactl", "list", "short", "sources"], 
                               capture_output=True, text=True)
        mics = bool(result.stdout.strip())
        if not speakers:
            print(""" 
                ❌ Mic not detected!
                Troubleshoot mic:
                    • No mic detected. RPi-specific checks:
                    • 1. Ensure mic is connected properly
                    • 2. Check ALSA: arecord -l
                    • 3. Verify PulseAudio detected it: pactl list sources
                    • 4. For USB mics: lsusb to check detection
            """)
        
        return mics, speakers
    except FileNotFoundError:
        print("pactl not found - PulseAudio may not be installed")
        return False, False

has_mic, has_speaker = check_pulseaudio_devices()