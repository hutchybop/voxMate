from pydub import AudioSegment

hey = AudioSegment.from_file("hey.mp3")
beep = AudioSegment.from_file("beep.mp3")

combined = hey + beep  # Concatenate audio

combined.export("combined.mp3", format="mp3")