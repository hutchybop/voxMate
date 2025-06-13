# voxMate ![voxMate Logo](voxMate_web_app/static/images/voxMate.png)

**voxMate** is a Python-powered smart speaker program that listens to your voice, processes it with AI, and responds with natural speech. It currently uses [Whisper](https://github.com/openai/whisper) via the [Groq API](https://groq.com/), sends your query to [Mistral AI](https://mistral.ai/) via the Groq API for intelligent responses, and speaks back using [gTTS](https://pypi.org/project/gTTS/).

> Think of it as your own DIY voice assistant — local, hackable, and growing.

---

## 🔧 Features

- 🎤 **Voice input** with your microphone (via `sounddevice`)
- 🧠 **Speech-to-text** with Whisper using the Groq API
- 💬 **Conversational AI** with Mistral via Groq
- 🔊 **Text-to-speech** using gTTS (Google Text-to-Speech)
- 💻 Built entirely in **Python**
- 🚧 Extensible for future features (Spotify, smart home control, web GUI, etc.)

---

## 📦 Requirements

- Python 3.9+
- Groq API key (for Whisper & Mistral)
- Internet connection (for gTTS and API calls)

---

## Current Workflow

voxMate will:
- Listen to your voice
- Transcribe it
- Send it to Mistral for a response
- Speak the reply aloud

---

## 📍 Roadmap

Planned features:

🎵 Spotify voice control
🌐 Web GUI for settings & logs
🏠 Smart home integration (e.g., lights, thermostat)
🧠 Personality modes (e.g., witty, helpful, quiet)
🗂 Local/remote database for commands or memory

---

## Contributing

This project is still a work in progress. Feedback, feature requests, and contributions are welcome!

Feel free to open issues or submit pull requests with:

- Suggestions for UI/UX improvements.
- New feature ideas.
- Bug reports.

---