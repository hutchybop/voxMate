import subprocess
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class AudioChecker:
    """Class to check audio devices on Raspberry Pi with PulseAudio"""
    suggestions: Dict[str, List[str]] = field(default_factory=lambda: {
        'global': [],
        'mic': [],
        'speaker': []
    })
    
    def __post_init__(self):
        self.devices = {'mic': False, 'speaker': False}
        self._check_audio()

    def _run_command(self, cmd: List[str]) -> str:
        """Helper to run shell commands safely"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.suggestions['global'].append(f"Command failed: {' '.join(cmd)} - {e.stderr.strip()}")
            return ""

    def _check_pulseaudio(self) -> bool:
        """Check if PulseAudio is available"""
        if not self._run_command(["which", "pactl"]):
            self.suggestions['global'].extend([
                "PulseAudio not found. Install with:",
                "sudo apt install pulseaudio pavucontrol",
                "For RPi audio: sudo apt install pulseaudio-module-alsa"
            ])
            return False
        return True

    def _check_audio(self):
        """Main check logic"""
        if not self._check_pulseaudio():
            return

        output = self._run_command(["pactl", "list", "short"])
        self.devices['mic'] = "Source" in output
        self.devices['speaker'] = "Sink" in output

        if not self.devices['mic']:
            self.suggestions['mic'].extend([
                "No microphone detected. Try:",
                "1. Check connections: arecord -l",
                "2. sudo raspi-config > Advanced > Audio",
                "3. pacmd set-default-source <name>"
            ])

        if not self.devices['speaker']:
            self.suggestions['speaker'].extend([
                "No speakers detected. Try:",
                "1. Check audio jack/HDMI connection",
                "2. sudo raspi-config > System Options > Audio",
                "3. amixer -D pulse sset Master unmute"
            ])

    def display_results(self):
        """Display results in user-friendly format"""
        status = {
            'mic': "✅" if self.devices['mic'] else "❌",
            'speaker': "✅" if self.devices['speaker'] else "❌"
        }
        
        print(f"\nRPi Audio Status:\nMic: {status['mic']}  Speaker: {status['speaker']}\n")
        
        for device in ['mic', 'speaker']:
            if not self.devices[device] and self.suggestions.get(device):
                print(f"Troubleshoot {device}:")
                print('\n'.join(f"• {s}" for s in self.suggestions[device]))
        
        if self.suggestions.get('global'):
            print("\nSystem-wide issues:")
            print('\n'.join(f"• {s}" for s in self.suggestions['global']))

# Usage
checker = AudioChecker()
checker.display_results()