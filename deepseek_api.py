from datetime import datetime
from openai import OpenAI


def get_response(message, save_chat, api_key, model="deepseek-chat"):

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role":"user", "content":message}
    ]

    chat_response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=2000,
        stream=False
    )

    if save_chat:
        chat = "Message:\n" + message + """\n---\n""" + "Response:\n" + chat_response.choices[0].message.content
        with open(f"completions/chat_{datetime.now().strftime('%d-%m-%Y_%H:%M:%S')}.txt", "w") as f:
            f.write(chat)

    return chat_response.choices[0].message.content
