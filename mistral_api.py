import os
import toml
from datetime import datetime
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

def get_response(message, save_chat, api_key, model):

    client = MistralClient(api_key=api_key)

    messages = [
        ChatMessage(role="user", content=message)
    ]

    # No streaming
    chat_response = client.chat(
        model=model,
        messages=messages,
    )

    if save_chat:
        chat = "Message:\n" + message + """\n---\n""" + "Response:\n" + chat_response.choices[0].message.content
        with open(f"completions/chat_{datetime.now().strftime('%d-%m-%Y_%H:%M:%S')}.txt", "w") as f:
            f.write(chat)

    return chat_response.choices[0].message.content

