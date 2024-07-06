"""
backend/setup_openai_assistant.py

Use this script to create a new OpenAI assistant with the fine-tuned model and the required tools for the SongScope.
If you made new functions or made changes to the existing functions, you can update the assistant with the new tools.

Attention: Put the new id in the .env file as well
"""

import os
import openai
from dotenv import load_dotenv
from backend import SYSTEM_PROMPT, AI_MODEL

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")

OPENAI_CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)

functions = [
    {
        "type": "function",
        "function": {
            "name": "search_track_on_spotify",
            "description": "THIS FUNCTION MUST BE CALLED FOR EVERY SINGLE SONG RECOMMENDATION WITHOUT EXCEPTION. It "
                           "searches for a track on Spotify and returns the official Spotify URL. DO NOT provide any "
                           "song"
                           "recommendations or Spotify links without using this function.",
            "parameters": {
                "type": "object",
                "properties": {
                    "track_name": {
                        "type": "string",
                        "description": "The exact name of the track to search for. This is required."
                    },
                    "artist_name": {
                        "type": "string",
                        "description": "The exact name of the artist. This is required."
                    }
                },
                "required": ["track_name", "artist_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "Search for reviews and information about a song or artist on Pitchfork.com",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The song and artist to search for on Pitchfork.com"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "The maximum number of results to return (optional)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    }
    ,

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


def create_openai_assistant():
    """
    Create a new OpenAI assistant with the fine-tuned model and the required tools for the SongScope.

    Returns:
    str: The ID of the newly created assistant.
    """
    assistant = OPENAI_CLIENT.beta.assistants.create(
        name="SongScope Assistant with Fine-Tuned Model",
        instructions=SYSTEM_PROMPT,
        tools=functions,
        model=AI_MODEL
    )
    # Return the ID of the newly created assistant
    return assistant.id


def update_openai_assistant(assistant_id):
    """
    Update an existing OpenAI assistant with the required tools for the SongScope.

    :param assistant_id: The ID of the assistant to update.
    :return: The ID of the updated assistant.
    """
    assistant = OPENAI_CLIENT.beta.assistants.update(
        assistant_id,
        tools=functions
    )
    # Return the ID of the updated assistant
    return assistant.id


if __name__ == "__main__":
    new_id = create_openai_assistant()
    # set the environment variable to the new assistant ID

    # use this if you want to update a pre-existing assistant
    # new_id = update_openai_assistant("your-assistant-id")
    os.environ["OPEN_AI_ASSISTANT_ID"] = new_id
