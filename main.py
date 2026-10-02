"""Run the JARVIS voice assistant."""

import os
import shutil
from pathlib import Path

import speech_recognition as sr
from deepgram import DeepgramClient
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from openai import OpenAI

from chat import ask_chatgpt, reset_conversation
from speech_to_text import speech_to_text
from text_to_speech import text_to_speech


def load_api_keys() -> dict[str, str]:
    """Read credentials from the environment or the project's .env file."""
    load_dotenv(Path(__file__).with_name(".env"))
    names = ("OPENAI_API_KEY", "DEEPGRAM_API_KEY", "ELEVENLABS_API_KEY")
    keys = {name: os.getenv(name, "").strip() for name in names}
    missing = [name for name, value in keys.items() if not value]
    if missing:
        raise SystemExit(
            "Missing API keys: " + ", ".join(missing)
            + ". Copy .env.example to .env and fill in your credentials."
        )
    return keys


def main() -> None:
    """Wait for a wake phrase, then handle a spoken conversation."""
    keys = load_api_keys()
    if shutil.which("mpv") is None:
        raise SystemExit("Install mpv and add it to PATH for audio playback.")

    deepgram_client = DeepgramClient(keys["DEEPGRAM_API_KEY"])
    openai_client = OpenAI(api_key=keys["OPENAI_API_KEY"])
    elevenlabs_client = ElevenLabs(api_key=keys["ELEVENLABS_API_KEY"])
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print('Say "hey Jarvis" or "hello Jarvis" to begin.')
    print('Say "shut down" while waiting, or press Ctrl+C, to exit.')

    try:
        while True:
            try:
                with microphone as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    print("Listening for a wake phrase...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

                text = recognizer.recognize_google(audio).lower()
                print(f"You said: {text}")

                if "hey jarvis" in text or "hello jarvis" in text:
                    text_to_speech(
                        elevenlabs_client, "Hello sir! How can I help you today?"
                    )
                    while True:
                        question = speech_to_text(deepgram_client)
                        if not question:
                            print("No question received. Returning to the wake phrase.")
                            reset_conversation()
                            break

                        print(f"You: {question}")
                        answer = ask_chatgpt(openai_client, question)
                        if answer:
                            print(f"JARVIS: {answer}")
                            text_to_speech(elevenlabs_client, answer)

                        if "goodbye" in question.lower() or "thank you" in question.lower():
                            reset_conversation()
                            break
                elif "shut down" in text:
                    break

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                print("I could not understand you. Please speak again.")
            except sr.RequestError:
                print("Wake phrase recognition failed. Check your internet connection.")
            except Exception as error:
                reset_conversation()
                print(f"An unexpected error occurred ({type(error).__name__}).")

    except KeyboardInterrupt:
        print("\nJARVIS stopped.")


if __name__ == "__main__":
    main()
