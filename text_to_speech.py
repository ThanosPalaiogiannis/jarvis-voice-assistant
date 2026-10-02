"""Stream spoken responses through ElevenLabs."""

from elevenlabs import stream
from elevenlabs.client import ElevenLabs

VOICE_ID = "TX3LPaxmHKxFdv7VOQHJ"
MODEL = "eleven_multilingual_v2"


def text_to_speech(client: ElevenLabs, text: str) -> None:
    """Generate and play speech without saving audio files."""
    audio_stream = client.generate(
        text=text,
        stream=True,
        model=MODEL,
        voice=VOICE_ID,
    )
    stream(audio_stream)
