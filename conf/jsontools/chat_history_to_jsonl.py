"""
In here i will store the chat history in a jsonl file
as well (in addition to being stored in chroma)

This is done for experimentation purposes to use it
maybe for fine tuning jobs or training.

"""
import json
import os

from backend import SYSTEM_PROMPT


def chat_history_to_jsonl(thread_id, message, response):
    prompt = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ]
    }

    filename = f'data/chat_history_as_jsonl/{thread_id}.jsonl'

    with open(filename, 'a') as f:
        json_line = json.dumps(prompt)
        f.write(json_line + '\n')

    return f"Chat history saved to {filename}"
