# Prepare data for fine-tuning
"""
conf/finetuning/prompts.py

This file is for generating prompts for the training data file. The prompts are generated from the recommendations
in the MongoDB database. Pay attention that this wouldn't work if the collection is empty.

Use the output (prompts.jsonl) in the finetuning.py or in the OpenAI interface to fine-tune the model.

"""
import uuid

from conf.mongodb import query
from conf import MONGODB_CLIENT, DB_NAME
import json
from collections import defaultdict
from backend import SYSTEM_PROMPT


def recommendations_to_prompts(query_result):
    if query_result is None:
        # Get all recommendations from the database
        query_result = query.collection_query_all(MONGODB_CLIENT, DB_NAME, "recommendations")

    # Initialize a defaultdict to group tracks
    tracks = defaultdict(list)

    # Parse each JSON string and add to the appropriate group
    for json_str in query_result:
        data = json.loads(json_str)

        # Use default values if keys are missing
        acousticness = data.get("target_acousticness", 0.0)
        instrumentalness = data.get("target_instrumentalness", 0.0)
        popularity = data.get("target_popularity", 0)
        tempo = data.get("target_tempo", 0.0)

        key = (acousticness, instrumentalness, popularity, tempo)
        tracks[key].append(data)

    # Convert defaultdict to regular dict
    grouped_tracks = dict(tracks)

    # Create prompts based on the grouped tracks
    system_prompt = SYSTEM_PROMPT
    prompts = []

    for weights, songs in grouped_tracks.items():
        user_prompt = (f"Recommend me a song. A song with these characteristics:"
                       f"Acousticness: {weights[0]}, Instrumentalness: {weights[1]}, Popularity: {weights[2]}, Tempo: {weights[3]}")
        response = "Recommended songs:\n"

        for song in songs:
            song_details = (
                f"Name: {song['name']}, "
                f"Album: {song['album']}, "
                f"Artists: {', '.join(song['artists'])}, "
                f"Duration: {song['duration_ms']} ms, "
                f"Explicit: {song['explicit']}, "
                f"Popularity: {song['popularity']}, "
                f"Preview URL: {song['preview_url']}, "
                f"Spotify URL: {song['external_urls']['spotify']}"
            )
            response += song_details + "\n"

        prompt = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": response.strip()}
            ]
        }

        prompts.append(prompt)

    return prompts


def save_prompts_to_jsonl(prompts, filename):
    with open(filename, 'w') as f:
        for prompt in prompts:
            json_line = json.dumps(prompt)
            f.write(json_line + '\n')


if __name__ == "__main__":
    # Query the database for recommendations
    recommendations = query.collection_query_all(MONGODB_CLIENT, DB_NAME, "recommendations")
    print(f"Recommendations collection queried. Total recommendations: {len(recommendations)}")

    # Generate the prompts
    prompts = recommendations_to_prompts(recommendations)
    print(f"Prompts for training the model generated. Total prompts: {len(prompts)}")

    # Save the prompts to a JSONL file
    save_prompts_to_jsonl(prompts, f'../data/training_data/prompts.jsonl')

    print(f"JSONL file have been saved to prompts.jsonl")
