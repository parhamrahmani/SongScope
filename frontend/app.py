"""
frontend/app.py

handles the communication between the frontend and the backend. It uses the Chainlit library to create a chat interface
that communicates with the backend. The chat interface is used to interact with the OpenAI API to provide assistance to
the user.

"""
from urllib.parse import urlparse, parse_qs

import chainlit as cl
from backend import OPENAI_API_KEY, OPENAI_CLIENT, AI_MODEL, OPEN_AI_ASSISTANT_ID
import requests
import os
import subprocess

import chainlit as cl
import requests
from urllib.parse import parse_qs, urlparse

import chainlit as cl
import requests
import os
import threading

BACKEND_URL = "http://localhost:5000"


def get_thread_by_name(name):
    for thread in threading.enumerate():
        if thread.name == name:
            return thread
    return None


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("access_token", os.environ.get('SPOTIFY_ACCESS_TOKEN'))
    cl.user_session.set("refresh_token", os.environ.get('SPOTIFY_REFRESH_TOKEN'))
    cl.user_session.set("expires_at", os.environ.get('SPOTIFY_EXPIRES_AT'))

    thread = OPENAI_CLIENT.beta.threads.create()
    cl.user_session.set("thread_id", thread.id)


@cl.on_message
async def on_message(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")
    access_token = cl.user_session.get("access_token")

    if access_token is not None:
        print(f"Using session ID: {access_token}")  # Debug print
    else:
        await cl.Message(content="Error: No access token available. Please log in again.").send()
        return

    response = requests.post(
        f"{BACKEND_URL}/chat",
        json={"thread_id": thread_id, "message": message.content},
        cookies={'access_token': access_token}
    )

    if response.status_code != 200:
        await cl.Message(content=f"Error processing your request. Status code: {response.status_code}").send()
    else:
        try:
            data = response.json()
            if data['status'] == 'success':
                await cl.Message(content=data['message']).send()
            else:
                await cl.Message(content=f"Error: {data.get('message', 'Unknown error')}").send()
        except Exception as e:
            await cl.Message(content=f"Error processing the response: {str(e)}").send()


def run_chainlit():
    print("Starting Chainlit server")
    os.environ["CHAINLIT_NO_BROWSER"] = "true"
    os.environ["PORT"] = "8000"
    subprocess.run(["chainlit", "run", __file__, "--host", "0.0.0.0", "--port", "8000", "--headless"], check=True)


if __name__ == '__main__':
    run_chainlit()
