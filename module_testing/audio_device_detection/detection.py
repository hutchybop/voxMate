import subprocess
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class AudioChecker:
    """Audio device checker for Ubuntu Server on RPi"""
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
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip()
        except FileNotFoundError:
            self.suggestions['global'].append(f"Command not found: {cmd[0]}")
            return ""

    def _check_pulseaudio(self) -> bool:
        """Check if PulseAudio is available and running"""
        if not self._run_command(["which", "pactl"]):
            self.suggestions['global'].extend([
                "PulseAudio not installed. Install with:",
                "sudo apt update && sudo apt install -y pulseaudio"
            ])
            return False
        
        # Check if PulseAudio is running
        if "Connection refused" in self._run_command(["pactl", "list"]):
            self.suggestions['global'].extend([
                "PulseAudio not running. Try:",
                "pulseaudio --start --log-level=1",
                "For system-wide: sudo systemctl enable --user pulseaudio"
            ])
            return False
            
        return True

    def _check_audio(self):
        """Main check logic for Ubuntu Server"""
        if not self._check_pulseaudio():
            return

        # Check devices
        output = self._run_command(["pactl", "list", "short"])
        self.devices['mic'] = "Source" in output
        self.devices['speaker'] = "Sink" in output

        # Ubuntu Server specific suggestions
        if not self.devices['mic']:
            self.suggestions['mic'].extend([
                "No microphone detected. Try:",
                "1. Check physical connections",
                "2. List ALSA devices: arecord -l",
                "3. Verify PulseAudio detected it: pactl list sources",
                "4. For USB mics: lsusb to check detection"
            ])

        if not self.devices['speaker']:
            self.suggestions['speaker'].extend([
                "No output devices detected. Try:",
                "1. Check audio connections (HDMI/3.5mm)",
                "2. List ALSA devices: aplay -l",
                "3. Set default sink: pacmd set-default-sink <name>",
                "4. Check volume: amixer -D pulse sset Master 100% unmute"
            ])

    def display_results(self):
        """Display results in user-friendly format"""
        status = {
            'mic': "✅" if self.devices['mic'] else "❌",
            'speaker': "✅" if self.devices['speaker'] else "❌"
        }
        
        print(f"\nAudio Status (Ubuntu Server):\nMic: {status['mic']}  Speaker: {status['speaker']}\n")
        
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