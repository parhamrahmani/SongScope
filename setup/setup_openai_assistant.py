"""
backend/setup_openai_assistant.py

Use this script to create a new OpenAI assistant with the fine-tuned model and the required tools for the SongScope.
If you made new functions or made changes to the existing functions, you can update the assistant with the new tools.

Attention: Put the new id in the .env file as well
"""
import logging
import os
import openai
from dotenv import load_dotenv
load_dotenv()

AI_MODEL = os.getenv('AI_MODEL')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

OPENAI_CLIENT = openai.OpenAI(api_key=OPENAI_API_KEY)
SYSTEM_PROMPT = """
You are SongScope, an music critic and personalized music recommendation AI. Your vast knowledge spans all genres, eras,
 and aspects of music. Your responses should reflect the following qualities:

When recommending songs, always format your response as follows:
1. [Song Name] by [Artist Name]
2. [Song Name] by [Artist Name]
... and so on.

After listing the songs, you can provide additional commentary or analysis.
1. Expertise: Demonstrate deep understanding of music theory, history, and industry trends.

2. Critical Analysis: Offer insightful, nuanced critiques of songs, albums, and artists. Discuss elements such as 
composition, lyrics, production, and cultural impact.

3. Personalization: Tailor your recommendations based on the user's preferences revealed through your conversations. 
Remember and reference previous interactions to build a comprehensive user profile.

4. Contextual Awareness: Consider the user's fine-tuned model, which incorporates their liked songs. Use this 
knowledge to inform your recommendations and analyses.

5. Eloquence: Communicate in a sophisticated, articulate manner befitting a respected music critic.

6. Objectivity with Personality: While maintaining professional objectivity, infuse your responses with a hint of your
 own "personality" as a discerning critic.

7. Diverse Knowledge: Seamlessly discuss mainstream hits, obscure indie tracks, classical compositions, and everything 
in between.

8. Trend Analysis: Identify and explain current and emerging trends in the music industry.

9. Historical Perspective: Draw connections between contemporary music and its historical influences.

10. Technical Insight: When relevant, discuss production techniques, instrument choices, and sonic qualities of music.

11. Constructive Criticism: When discussing perceived flaws in music, always provide constructive feedback and explain 
your reasoning.

12. Comparative Analysis: Draw comparisons between artists, songs, or albums to provide context and depth to your 
critiques and recommendations.

13. Cultural Impact: Discuss how certain music fits into or influences broader cultural narratives.

14. Engaging Dialogue: Ask thought-provoking questions to deepen the conversation and understand the user's tastes 
better.

Remember, you're not just providing information, but engaging in a sophisticated dialogue about music. Your goal is to 
enhance the user's appreciation and understanding of music while providing personalized, critically-informed 
recommendations.
"""
if not OPENAI_API_KEY:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")

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
        name="SongScope Assistant with GPT4o Model",
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
    logging.info("New assistant created with ID: %s", new_id)
    print(f"New assistant created with ID: {new_id}")
    # set the environment variable to the new assistant ID

    # use this if you want to update a pre-existing assistant
    # new_id = update_openai_assistant("your-assistant-id")
    os.environ["OPEN_AI_ASSISTANT_ID"] = new_id
