# Need to install piper locally
# Instructions at: https://github.com/rhasspy/piper
# Slow on RPi4

import subprocess
import re
import select
import signal

class PiperTTS:
    def __init__(self):
        self._init_piper()
        signal.signal(signal.SIGINT, self._cleanup)
        signal.signal(signal.SIGTERM, self._cleanup)

    def _init_piper(self):
        # Start Piper once with line-buffered output
        self.piper_proc = subprocess.Popen(
            [
                "piper",
                "--model", "/home/hutch/smartSpeaker/voices/en_GB-alba-medium.onnx",
                "--output_file", "-"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=1,  # Line-buffered
            universal_newlines=False
        )

    def _cleanup(self, signum=None, frame=None):
        if self.piper_proc.poll() is None:
            self.piper_proc.stdin.close()
            self.piper_proc.terminate()
            self.piper_proc.wait()
        exit(0)

    def synthesize(self, text):
        # Clean text
        clean_text = re.sub(r"\*\*(.*?)\*\*|[_*~]", r"\1", text)
        
        # Send text with flush marker
        self.piper_proc.stdin.write(clean_text.encode() + b"\n")
        self.piper_proc.stdin.flush()

        # Read audio until we get a complete chunk
        audio_data = b""
        while True:
            # Use poll to check if output is ready
            rlist, _, _ = select.select([self.piper_proc.stdout], [], [], 0.5)
            
            if rlist:
                chunk = self.piper_proc.stdout.read1(4096)
                if not chunk:
                    break
                audio_data += chunk
                # Check for end of audio (Piper might not close stream)
                if len(chunk) < 4096:
                    break
            else:
                # Timeout or process ended
                if self.piper_proc.poll() is not None:
                    break
                if audio_data:
                    break  # Return what we have

        return audio_data

if __name__ == "__main__":
    tts = PiperTTS()
    
    try:
        while True:
            quest = input("What do you want to say? Type 'stop' to finish: ")
            if quest.lower() == 'stop':
                break
            
            audio = tts.synthesize(quest)
            if audio:
                aplay = subprocess.Popen(
                    ["aplay", "-"],
                    stdin=subprocess.PIPE
                )
                aplay.communicate(input=audio)
    finally:
        tts._cleanup()