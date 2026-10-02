"""Transcribe one spoken question using Deepgram's WebSocket API."""

import threading

from deepgram import DeepgramClient, LiveOptions, LiveTranscriptionEvents, Microphone


def speech_to_text(client: DeepgramClient) -> str | None:
    """Listen until a completed utterance arrives, then release the microphone."""
    final_parts = []
    final_text = ""
    finished = threading.Event()
    connection = None
    microphone = None

    def on_message(_client, result, **_kwargs):
        nonlocal final_text
        sentence = result.channel.alternatives[0].transcript
        if not sentence:
            return
        if result.is_final:
            final_parts.append(sentence)
            if result.speech_final:
                final_text = " ".join(final_parts)
                finished.set()

    def on_utterance_end(_client, utterance_end, **_kwargs):
        nonlocal final_text
        if final_parts:
            final_text = " ".join(final_parts)
            finished.set()

    def on_error(_client, error, **_kwargs):
        print("Deepgram transcription failed.")
        finished.set()

    def on_close(_client, close, **_kwargs):
        finished.set()

    try:
        connection = client.listen.websocket.v("1")
        connection.on(LiveTranscriptionEvents.Transcript, on_message)
        connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
        connection.on(LiveTranscriptionEvents.Error, on_error)
        connection.on(LiveTranscriptionEvents.Close, on_close)

        options = LiveOptions(
            model="nova-2",
            language="en",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            interim_results=True,
            utterance_end_ms="1000",
            vad_events=True,
            endpointing=300,
        )

        if connection.start(options, addons={"no_delay": "true"}) is False:
            print("Failed to connect to Deepgram.")
            return None

        microphone = Microphone(connection.send)
        if microphone.start() is False:
            print("Failed to start the microphone.")
            return None

        print("Listening for your question...")
        finished.wait()
        return final_text or None

    except Exception as error:
        print(f"Speech recognition failed ({type(error).__name__}).")
        return None
    finally:
        try:
            if microphone is not None:
                microphone.finish()
        finally:
            if connection is not None:
                connection.finish()
