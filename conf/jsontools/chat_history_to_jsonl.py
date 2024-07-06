"""
In here i will store the chat history in a jsonl file
as well (in addition to being stored in chroma)

This is done for experimentation purposes to use it
maybe for fine tuning jobs or training.

"""
import json
from backend import SYSTEM_PROMPT


def chat_history_to_jsonl(thread_id, message, response):
    """
    This function saves the chat history to a jsonl file. This might be useful for training or fine-tuning.
    :param thread_id:  The ID of the thread where the chat history is saved.
    :param message:  The message from the user.
    :param response:  The response from the assistant.
    :return:  A message indicating the chat history is saved.
    """
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
