## 🚀 Deployment

### 🧰 Requirements

- 🐍 Python 3.9 or higher
- 🌐 [MongoDB Atlas](https://www.mongodb.com/atlas/database) account and database (or [local MongoDB](https://www.mongodb.com/docs/manual/installation/))
- 🧠 [Groq API key](https://console.groq.com/keys) for Whisper & Mistral
- 🗣 [Picovoice Porcupine API key](https://console.picovoice.ai/) for wake word detection
- 🔑 A `SECRET_KEY` for Flask session handling
- 🧪 Raspberry Pi 4 (tested) running Ubuntu Server 22.04 or higher

---

### 📦 Install System Dependencies

If deploying on a Raspberry Pi (or similar Debian-based system):

```bash
sudo apt update && sudo apt -y upgrade

sudo apt install -y \
  python3-pip python3-dev python3.13-venv build-essential \
  libffi-dev libssl-dev libasound2-dev \
  portaudio19-dev libportaudio2 libsndfile1 \
  ffmpeg libespeak1 curl unzip sox \
  libsox-fmt-mp3 mpg321 cmake libopenblas-dev alsa-utils
```

> ✅ Raspberry Pi OS users may also need: `libatlas-base-dev` and `libespeak-ng-dev`

---

### 🐍 Python Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 🛠 Environment Variables

Copy the example file and edit it with your settings:

```bash
cp .env.example .env
```

#### Required `.env` values:

| Key             | Description                                           |
|----------------|-------------------------------------------------------|
| `MONGO_URI`     | Your MongoDB connection URI (Atlas or local)         |
| `GROQ_API_KEY`  | API key from [Groq Console](https://console.groq.com/) |
| `WAKE_API_KEY`  | API key from [Picovoice Console](https://console.picovoice.ai/) |
| `SECRET_KEY`    | A secret string for Flask session signing            |

---

### 🌐 MongoDB Setup

- If using [MongoDB Atlas](https://www.mongodb.com/atlas/database):
  - Create a free-tier cluster
  - Whitelist your IP
  - Create a user and database
  - Copy the connection string and set it as `MONGO_URI` in `.env`

- Alternatively, install [MongoDB Community Edition](https://www.mongodb.com/docs/manual/installation/) locally.

---

### 🔑 API Keys

- **Groq API Key**:
  - Sign up at [Groq](https://groq.com/)
  - Go to [Groq Console](https://console.groq.com/)
  - Generate an API key

- **Porcupine Wake Word API Key**:
  - Sign up at [Picovoice Console](https://console.picovoice.ai/)
  - Create a Porcupine access key
  - Download the `.ppn` file for your platform (e.g. Raspberry Pi)

---

### ⚙️ Using the Web App (Optional)

The web app is used to set custom `voxMate` settings and persists them in MongoDB.

Settings currently supported:

- `silence_threshold`
- `silence_duration`
- `noise_reduction` (true/false)
- `stt_model` (e.g., `whisper-large`)
- `ai_model` (e.g., `mixtral-8x7b`)

> If the web app is not configured, `voxMate.py` will use default values.

🟡 **Note**: No API keys are stored or managed through the web app.

---

### 🤖 STT & AI Models (via Groq)

- **STT Model**: [Whisper](https://github.com/openai/whisper) (use `"whisper-large"` or other variants)
- **AI Model**: [Mistral](https://mistral.ai/news/mixtral-of-experts/), served via Groq

🆓 Groq’s free-tier gives access to powerful models for developers. More info:
- [Groq Docs](https://docs.groq.com/)
- [Groq Playground](https://console.groq.com/playground)

---

### 📡 Running on Raspberry Pi

voxMate has been tested on a Raspberry Pi 4 using Ubuntu Server. To configure audio:

```bash
aplay -l   # List speaker devices
arecord -l # List mic devices
```

#### Set Default Audio Device

Create or edit `~/.asoundrc`:

```
defaults.pcm.card 1
defaults.ctl.card 1
```

#### Test recording/playback:

```bash
arecord -D plughw:<card>,<device> -f cd -d 5 test.wav
aplay test.wav
```

---

### 🧠 How voxMate Works

1. Listens for a wake word (via Porcupine)
2. Records speech
3. Transcribes with Whisper via Groq
4. Sends transcript to Mistral via Groq
5. Speaks the response aloud using gTTS

---

### 📍 Future Plans

- 🎵 Spotify voice integration
- 🧠 Personality modes
- 🏡 Smart home features
- 🌐 Improved Web UI