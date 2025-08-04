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


def get_json_response(message, save_chat, api_key, model="gpt-4o", expect_json=True):

    if model not in ["gpt-4o", "gpt-4-turbo"]:
        raise ValueError("Unsupported model. Please use 'gpt-4o' or 'gpt-4-turbo'.")

    client = OpenAI(api_key=api_key)

    messages = [
        {"role": "user", "content": message}
    ]

    # Use response_format="json" if JSON output is expected (only supported by GPT-4-turbo or GPT-4o)
    response_args = {
        "model": model,
        "messages": messages,
        "max_tokens": 2000,
        "response_format": { "type": "json_object" },
    }

    chat_response = client.chat.completions.create(**response_args)

    content = chat_response.choices[0].message.content

    # Save chat to file if requested
    if save_chat:
        chat = "Message:\n" + message + "\n---\n" + "Response:\n" + content
        with open(f"completions/chat_{datetime.now().strftime('%d-%m-%Y_%H:%M:%S')}.txt", "w", encoding="utf-8") as f:
            f.write(chat)

    return content