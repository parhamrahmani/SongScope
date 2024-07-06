"""
initial_setup/mongodb_initial_setup.py

This script is used to setup the MongoDB database and collections for the Spotify data.
It also inserts example data into the collections. This data is inserted only for testing purposes.
You can delete the example data and insert your own data into the collections.

"""
import logging

import pymongo
from pymongo import MongoClient
from conf.mongodb.setup import (
    setup_db,
    setup_collections
)
from conf.mongodb.insertion import (insert_tracks,
                                    insert_albums,
                                    insert_artists,
                                    insert_playlist)
from conf.jsontools.tools import extract_and_transform_tracks, extract_and_transform_playlists, \
    extract_and_transform_liked_songs
from conf.jsontools.tools import load_json

if __name__ == "__main__":
    # Load your data
    data = load_json('../data/examples/example_tracks.json')

    # Extract and transform the data
    tracks_json, albums_json, artists_json = extract_and_transform_tracks(data)

    MONGODB_CLIENT = MongoClient("mongodb://localhost:27017/")
    DB_NAME = "spotifydb"
    COLLECTIONS = ["liked_songs", "albums", "artists", "playlists", "recommendations"]

    # Setup database and collections
    setup_db(MONGODB_CLIENT, DB_NAME)
    setup_collections(MONGODB_CLIENT, DB_NAME, COLLECTIONS)
    logging.info(
        "Initial Database setup completed. Created database 'spotifydb' and collections 'liked_songs', 'albums', "
        "'artists', 'playlists', 'recommendations'.")

    # Insert example data
    logging.info("Inserting example data... Track Data")
    insert_tracks(MONGODB_CLIENT, DB_NAME, tracks_json)
    insert_albums(MONGODB_CLIENT, DB_NAME, albums_json)
    insert_artists(MONGODB_CLIENT, DB_NAME, artists_json)
    logging.info("First round of data insertion completed.")

    logging.info("Second round of data insertion... Playlist data")
    data = load_json('../data/examples/example_playlist.json')
    playlist_json = extract_and_transform_playlists(data)
    insert_playlist(MONGODB_CLIENT, DB_NAME, playlist_json)
    logging.info("Second round of data insertion completed.")

    logging.info("Third round of data insertion... Liked Songs data")
    data = load_json('../data/examples/example_liked_tracks.json')
    liked_songs_json = extract_and_transform_liked_songs(data)
    tracks_json, albums_json, artists_json = extract_and_transform_tracks(liked_songs_json)
    insert_tracks(MONGODB_CLIENT, DB_NAME, tracks_json)
    insert_albums(MONGODB_CLIENT, DB_NAME, albums_json)
    insert_artists(MONGODB_CLIENT, DB_NAME, artists_json)
    logging.info("Third round of data insertion completed.")

