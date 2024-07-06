"""
conf/finetuning/generate_data.py

This file only generates seed tracks from the liked_songs collection in the MongoDB database randomly.

we can't use all of the liked songs to generate recommendations because there is a limit of 5 seed tracks in each
recommendation request to the Spotify API. In this way we can generate a random seed tracks from the liked songs
that we have in the MongoDB database.

You can do this manually with more careful selection of the seed tracks, but for the purpose of this project we will
use random selection because we need large amount of data to train the model and to save time.

"""
import logging
import random
from conf import MONGODB_CLIENT, DB_NAME



def generate_seed_tracks(MONGODB_CLIENT, DB):
    """
    Generate 5 seed tracks randomly from the liked_songs collection in the MongoDB database.

    :param MONGODB_CLIENT: the MongoDB client
    :param DB: the name of the database we are using
    :return: the list of 5 seed tracks (Spotify track IDs)
    """
    logging.info("Generating seed tracks for generating Recommendations...\n"
                 "DB: %s , Collection: liked_songs",
                 DB)
    spotifydb = MONGODB_CLIENT[DB]
    liked_songs = spotifydb["liked_songs"]

    total_liked_songs = liked_songs.count_documents({})
    logging.info("Total liked songs in the collection: %s", total_liked_songs)

    # Generate 5 unique random indices
    random_indices = random.sample(range(total_liked_songs), 5)

    seed_tracks = []
    for random_index in random_indices:
        random_track = liked_songs.find().limit(-1).skip(random_index).next()
        logging.info("Random track: %s", random_track)
        seed_tracks.append(random_track["track_id"])

    return seed_tracks


if __name__ == "__main__":
    seed_tracks = generate_seed_tracks(MONGODB_CLIENT, DB_NAME)
    logging.info("Seed tracks: %s", seed_tracks)
