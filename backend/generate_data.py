import random
from conf import MONGODB_CLIENT, DB_NAME
from flask import session, redirect
from datetime import datetime

def generate_seed_tracks(MONGODB_CLIENT, DB):
    print("Getting random seed tracks from liked songs")
    spotifydb = MONGODB_CLIENT[DB]
    liked_songs = spotifydb["liked_songs"]

    total_liked_songs = liked_songs.count_documents({})
    print(f"Total liked songs: {total_liked_songs}")

    # Generate 5 unique random indices
    random_indices = random.sample(range(total_liked_songs), 5)

    seed_tracks = []
    for random_index in random_indices:
        random_track = liked_songs.find().limit(-1).skip(random_index).next()
        seed_tracks.append(random_track["track_id"])

    return seed_tracks


if __name__ == "__main__":
    seed_tracks = generate_seed_tracks(MONGODB_CLIENT, DB_NAME)
    print(seed_tracks)
