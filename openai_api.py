from datetime import datetime
from openai import OpenAI


def get_response(message, save_chat, api_key, model="gpt-3.5-turbo"):

    client = OpenAI(
        api_key=api_key,
    )

    messages = [
        {"role":"user", "content":message}
    ]

    chat_response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=2000,
    )

    if save_chat:
        chat = "Message:\n" + message + """\n---\n""" + "Response:\n" + chat_response.choices[0].message.content
        with open(f"completions/chat_{datetime.now().strftime('%d-%m-%Y_%H:%M:%S')}.txt", "w") as f:
            f.write(chat)

    return chat_response.choices[0].message.content

