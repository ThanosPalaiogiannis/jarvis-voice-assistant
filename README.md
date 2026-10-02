# JARVIS

I built JARVIS for my diploma thesis at the International Hellenic University.
It was my first Python project, developed on a Raspberry Pi 4 with a microphone
and a speaker.

You start a conversation by saying "hey Jarvis" or "hello Jarvis", ask a question,
and hear the answer spoken back. JARVIS keeps the conversation history until you
say "goodbye" or "thank you".

## How it works

- **SpeechRecognition** uses Google's online recognition service to listen for
  the wake phrase.
- **Deepgram** transcribes the question through a WebSocket connection.
- **OpenAI** generates an answer using the current conversation history.
- **ElevenLabs** streams the spoken answer, with `mpv` handling playback.

The conversation is configured for English. Each text answer is received in full
before speech playback starts, and no audio files are saved.

## Setup

You need Python 3.12, a microphone, speakers, an internet connection and API keys
for OpenAI, Deepgram and ElevenLabs. Audio playback also requires
[mpv](https://mpv.io/installation/) on your `PATH`.

Open a terminal in the project folder and follow the steps for your system.

### Raspberry Pi OS / Debian / Ubuntu

Install the audio dependencies:

```bash
sudo apt install python3-venv python3-dev portaudio19-dev mpv
```

With Python 3.12 installed, create a virtual environment and install the packages:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

If PyAudio fails to build, check that the Python development headers match the
Python version you are using.

### Windows (PowerShell)

Install Python 3.12 and `mpv`, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

### API keys

Fill in your local `.env` file:

```dotenv
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

The `.env` file is excluded from Git. Variables already set on your system take
precedence over values in the file.

## Run

With the virtual environment active:

```bash
python main.py
```

- Say **"hey Jarvis"** or **"hello Jarvis"** to start talking.
- Ask your questions in English.
- Say **"goodbye"** or **"thank you"** to end the conversation and clear its history.
- Say **"shut down"** while JARVIS is waiting for a wake phrase to exit.
- Press **Ctrl+C** to stop it at any time.

The conversation ends whenever "goodbye" or "thank you" appears in a question,
even as part of a longer sentence.

## Files

| File | What it does |
| --- | --- |
| `main.py` | Handles activation and connects the rest of the application. |
| `speech_to_text.py` | Captures and transcribes a question with Deepgram. |
| `chat.py` | Requests answers from OpenAI and manages conversation history. |
| `text_to_speech.py` | Generates and plays speech with ElevenLabs. |

Dependencies are listed in `requirements.txt`. Use `.env.example` as the template
for your credentials.

## Notes

The code keeps the model choices from the original thesis project:

- Deepgram: `nova-2`, English, mono audio at 16 kHz.
- OpenAI: `gpt-3.5-turbo` through Chat Completions.
- ElevenLabs: `eleven_multilingual_v2`, voice `TX3LPaxmHKxFdv7VOQHJ`.

Dependencies are pinned because the code uses older SDK interfaces. Access to the
models and voice depends on your service accounts. If a request fails, check your
credentials, quota and model availability. For audio issues, check the default
input/output devices and that `mpv` is available on `PATH`.
