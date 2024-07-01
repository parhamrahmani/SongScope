"""
# backend/chat.py

This file handles the requests to the chat endpoint and enables chatting with the AI assistant.
It also serves and renders the interface for the chat application.


"""
import json
import os
import threading
import time
import traceback
import re

import flask_session
import openai
from flask.sessions import SessionInterface

from backend import app, TAVILY_CLIENT, SYSTEM_PROMPT, AI_MODEL, OPENAI_API_KEY, OPENAI_CLIENT, OPEN_AI_ASSISTANT_ID
from flask import request, jsonify, redirect, render_template_string, render_template, session, make_response, url_for

from conf.jsontools.chat_history_to_jsonl import chat_history_to_jsonl
from conf.spotifyapi import spotifyauth
from conf.spotifyapi.spotfiyapi_functions import search_track_on_spotify
from conf.spotifyapi.spotifyauth import check_auth
from frontend.app import run_chainlit
from backend.functions import tavily_search, pitchfork_review
from chroma_db import insert_chat_message
import chainlit as cl

functions = [
    {
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "Get reviews and lyrics for a song.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The song and artist to search for."
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "pitchfork_review",
            "description": "Get reviews from Pitchfork for a song or the album of that song.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The song and artist to search for."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

function_lookup = {
    "tavily_search": tavily_search,
    "pitchfork_review": pitchfork_review
}

import json


def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_outputs_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = json.loads(tool.function.arguments)
        function_to_call = function_lookup[function_name]
        output = function_to_call(**function_args)
        if output:
            # Convert the output to a JSON string
            output_str = json.dumps(output)
            tool_outputs_array.append({"tool_call_id": tool_call_id, "output": output_str})

    return OPENAI_CLIENT.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs_array
    )


@app.route('/interface', methods=['GET'])
def interface():
    if 'access_token' not in session:
        return redirect('/login')

    if not any(thread.name == 'chainlit' for thread in threading.enumerate()):
        chainlit_thread = threading.Thread(target=run_chainlit, name='chainlit', daemon=True)
        chainlit_thread.start()
        time.sleep(3)
        print("Chainlit thread started.")

    return redirect(f'http://localhost:8000/?session_id={session.sid}')


@app.route('/chat', methods=['POST'])
def chat():
    print("Entering chat function")
    thread_id = request.json.get("thread_id")
    message = request.json.get("message")
    print("Thread ID: ", thread_id)
    print("Message: ", message)

    try:
        # Add the user's message to the thread
        OPENAI_CLIENT.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

        # Create a run
        run = OPENAI_CLIENT.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=OPEN_AI_ASSISTANT_ID)

        # Wait for the run to complete
        while run.status not in ["completed", "failed"]:
            print("Run status: ", run.status)
            time.sleep(1)
            run = OPENAI_CLIENT.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run.status == 'requires_action':
                run = submit_tool_outputs(thread_id, run.id, run.required_action.submit_tool_outputs.tool_calls)

        # Retrieve the assistant's messages
        messages = OPENAI_CLIENT.beta.threads.messages.list(thread_id=thread_id)

        if messages.data:
            assistant_message = messages.data[0]
            if assistant_message.content:
                text_content = assistant_message.content[0].text.value

                # Verify and enrich the recommendation

                # Intentionally using this here manually instead of adding it as function to the assistant
                # to observe the difference and effectivity
                verified_lines = []
                for line in text_content.split('\n'):
                    if "by" in line:
                        try:
                            song, artist = line.split("by")
                            song = song.strip()
                            artist = artist.strip()
                            print(f"Verifying track info: Song: {song}, Artist: {artist}")
                            track_info, error = search_track_on_spotify(song, artist)
                            if track_info:
                                print("Verified: ", line)
                                verified_lines.append(
                                    f"{track_info['name']} by {track_info['artists'][0]['name']} (Spotify URL: {track_info['external_urls']['spotify']})")

                            else:

                                verified_lines.append(f"{line}")
                        except ValueError:
                            print("Could not split the line: ", line)
                            continue
                    else:
                        verified_lines.append(line)

                verified_content = '\n'.join(verified_lines)

                # Add the verified content as a new assistant message
                OPENAI_CLIENT.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="assistant",
                    content=verified_content
                )

                # Store the conversation
                insert_chat_message(thread_id, message, verified_content, int(time.time()))
                chat_history_to_jsonl(thread_id, message, verified_content)

                print("Verified content: ", verified_content)

                return jsonify({"status": "success", "message": verified_content})
            else:
                return jsonify({"status": "error", "message": "No content in assistant's message"}), 500
        else:
            return jsonify({"status": "error", "message": "No messages found"}), 500

    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An error occurred"}), 500
