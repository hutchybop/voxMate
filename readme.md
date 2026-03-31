# ⚠️ Archived Project

### This repository has been archived and is no longer actively maintained.

- No new features or bug fixes will be added
- Issues and pull requests are no longer monitored
- If you’d like to continue development, feel free to fork the project.

Last maintained: 20260331

---
---

<p>
  <img src="voxMate_web_app/static/images/voxMate.png" alt="voxMate Logo" width="40" style="vertical-align: middle; border-radius: 50%; margin-right: 10px;">
  <span style="font-size: 2em; font-weight: bold; vertical-align: middle;">voxMate</span>
</p>

**voxMate** is a Python-powered smart speaker program that listens to your voice, processes it with AI, and responds with natural speech. It currently uses [Whisper](https://github.com/openai/whisper) via the [Groq API](https://groq.com/), sends your query to an AI model via the Groq API for intelligent responses, and speaks back using [gTTS](https://pypi.org/project/gTTS/).

> Think of it as your own DIY voice assistant — local, hackable, and growing.

<br>

---

## 🔧 Features

- 🎤 **Voice input** with your microphone (via `sounddevice`)
- 🧠 **Speech-to-text** with Whisper using the Groq API
- 💬 **Conversational AI** with AI models via Groq
- 🔊 **Text-to-speech** using gTTS (Google Text-to-Speech)
- 💻 Built entirely in **Python**
- 🚧 Extensible for future features (Spotify, smart home control, web GUI, etc.)

<br>

---

## Current Workflow

voxMate will:

1. Listens for a wake word (via Porcupine)
2. Records speech
3. Transcribes with Whisper via Groq
4. Sends transcript to an AI model via Groq
5. Speaks the response aloud using gTTS

<br>

---

## 🚀 Deployment

#### 🧰 Requirements

- 🐍 Python 3.9 or higher
- 🌐 [MongoDB Atlas](https://www.mongodb.com/atlas/database) account and database (or [local MongoDB](https://www.mongodb.com/docs/manual/installation/))
- 🧠 [Groq API key](https://console.groq.com/keys) for Whisper & AI models
- 🗣 [Picovoice Porcupine API key](https://console.picovoice.ai/) for wake word detection
- 🔑 A `SECRET_KEY` for Flask session handling
- 🧪 Raspberry Pi 4 (tested) running Ubuntu Server 22.04 or higher
- Internet connection (for gTTS and API calls)

<br>

#### 📦 Install System Dependencies

If deploying on a Raspberry Pi (or similar Debian-based system):

```bash
sudo apt update && sudo apt -y upgrade

sudo apt install -y \
  python3-pip python3-dev python3.13-venv build-essential \
  libffi-dev libssl-dev libasound2-dev \
  portaudio19-dev libportaudio2 libsndfile1 \
  ffmpeg libespeak1 curl unzip sox \
  libsox-fmt-mp3 mpg123 cmake libopenblas-dev alsa-utils
```

> ✅ Raspberry Pi OS users may also need: `libatlas-base-dev` and `libespeak-ng-dev`

<br>

#### 🐍 Python Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

<br>

#### 🛠 Environment Variables

Copy the env example file and edit it with your settings:

```bash
cp .env.example .env
```

<br>

##### Required `.env` values:

| Key                 | Description                                                     |
|---------------------|-----------------------------------------------------------------|
| `MONGO_URI`         | Your MongoDB connection URI (Atlas or local)                    |
| `GROQ_API_KEY`      | API key from [Groq Console](https://console.groq.com/)          |
| `PORCUPINE_API_KEY` | API key from [Picovoice Console](https://console.picovoice.ai/) |
| `SECRET_KEY`        | A secret string for Flask session signing                       |

<br>

#### 🌐 MongoDB Setup

- If using [MongoDB Atlas](https://www.mongodb.com/atlas/database):
  - Create a free-tier cluster
  - Whitelist your IP
  - Create a user and database

- Alternatively, install [MongoDB Community Edition](https://www.mongodb.com/docs/manual/installation/) locally.

- Copy the connection string and set it as `MONGO_URI` in `.env`

<br>

#### 🔑 API Keys

**Groq API Key**:

  - Sign up at [Groq](https://groq.com/)
  - Go to [Groq Console](https://console.groq.com/)
  - Generate an API key
  - Set it as `GROQ_API_KEY` in `.env`


**Porcupine Wake Word API Key**:

  - Sign up at [Picovoice Console](https://console.picovoice.ai/)
  - Create a Porcupine access key
  - Set it as `PORCUPINE_API_KEY` in `.env`

**Add custom Porcupine wake word**:

  - Create a Wake Word from the Start Building section
  - Download the `.ppn` and `LICENSE.txt` files for your platform (e.g. Raspberry Pi)
  - Add the files to `voxMate/models/porcupine_keywords`

<br>

#### 🤖 STT & AI Models (via Groq)

- STT and AI models can be amended via the Web App

- The STT and AI models are seved via [Groq](https://console.groq.com).
- A list of models can be found at [Groq Models](https://console.groq.com/docs/models)
- [Whisper](https://github.com/openai/whisper) TTS models have worked well in testing.



🆓 Groq’s free-tier gives access to powerful models for developers. More info:
- [Groq Docs](https://docs.groq.com/)
- [Groq Playground](https://console.groq.com/playground)

<br>

#### ⚙️ Using the Web App (Optional)

The web app is used to set custom `voxMate` settings and persists them in MongoDB.

Settings currently supported:

- `silence_threshold`
- `silence_duration`
- `noise_reduction` (true/false)
- `stt_model` (e.g., `whisper-large`)
- `ai_model` (e.g., `mixtral-8x7b`)

> If the web app is not configured, `voxMate.py` will use default values.

🟡 **Note**: No API keys are stored or managed through the web app.

<br>

#### 📡 Running on Raspberry Pi

voxMate has been tested on a Raspberry Pi 4 using Ubuntu Server. To configure audio:

```bash
aplay -l   # List speaker devices
arecord -l # List mic devices
```
<br>

##### Set Default Audio Device

Create or edit `~/.asoundrc` and set default audio devices:

```
defaults.pcm.card <pcm card number>
defaults.ctl.card <ctl card number>
```
<br>

##### Test recording/playback:

- Start a test 5 second record:
  
    ```
    arecord -D plughw:<card>,<device> -f cd -d 5 test.wav
    ```

- Play the recording back:
  
    ```
    aplay test.wav
    ```

<br>

---

### 🏃‍♂️ Run voxMate.py and voxMate_web_app

Open two separate terminal screens.

In the first one:
```bash
cd <voxMate/voxMate_web_app path location>
flask run
```
Access the web app at `http://127.0.0.1:5000/`



In the second one:
```bash
cd <voxMate root path location>
python3 voxmate.py
```
Say `<Wake word/phase>` to ask a question

<br>

---

## 🔮 Future Plans

- 🎵 Spotify voice integration
- 🧠 Personality modes
- 🏡 Smart home features
- 🌐 Improved Web UI

<br>

---

## 🤝 Contributing

This project is still a work in progress. Feedback, feature requests, and contributions are welcome!

Feel free to open issues or submit pull requests with:

- Suggestions for UI/UX improvements.
- New feature ideas.
- Bug reports.

<br>

---