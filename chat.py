"""Generate answers and keep the current conversation in memory."""

from openai import APIError, OpenAI

MODEL = "gpt-3.5-turbo"
SYSTEM_PROMPT = (
    "Your name is Jarvis. You are a kind, helpful, funny, witty and trustworthy "
    "assistant who helps people solve problems and answers their questions. "
    "Your creator is Thanasis Palaiogiannis, who made you for his diploma thesis. "
    "When the user says goodbye or thank you, greet them and end the conversation. "
    "Keep your answers relatively short and clear, suitable for spoken playback."
)

conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]


def reset_conversation() -> None:
    """Discard the previous conversation while keeping the system prompt."""
    conversation_history[:] = [{"role": "system", "content": SYSTEM_PROMPT}]


def ask_chatgpt(client: OpenAI, question: str) -> str | None:
    """Return an answer, adding a turn to history only after a successful request."""
    user_message = {"role": "user", "content": question}
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=conversation_history + [user_message],
        )
    except APIError as error:
        print(f"OpenAI request failed ({type(error).__name__}).")
        return None

    answer = response.choices[0].message.content
    if not answer:
        print("OpenAI returned an empty answer.")
        return None

    conversation_history.extend(
        [user_message, {"role": "assistant", "content": answer}]
    )
    return answer
