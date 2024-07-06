"""
conf/mongodb/insertion.py

This module contains functions to insert transformed data from Spotify API into MongoDB collections.

"""


import json
import logging


def insert_tracks(MONGODB_CLIENT, DB, data):
    """
    Insert transformed tracks data into the MongoDB database.
    :param MONGODB_CLIENT: the client to connect to the MongoDB database
    :param DB: the name of the database
    :param data: the transformed tracks data
    :return: a message indicating the success of the insertion
    """
    logging.info(f"Inserting tracks data into {DB}")
    spotifydb = MONGODB_CLIENT[DB]

    liked_songs = spotifydb["liked_songs"]

    # Convert JSON strings back to Python lists/dictionaries for insertion
    tracks = json.loads(data)

    # Insert data into collections
    for track in tracks:
        if liked_songs.count_documents({"track_id": track["track_id"]}, limit=1) == 0:
            logging.info(f"Inserting {track['name']} into liked_songs collection.")
            liked_songs.insert_one(track)
        else:
            logging.info(f"Track {track['name']} already exists in liked_songs collection.")

    logging.info("Inserted transformed tracks successfully.")


def insert_albums(MONGODB_CLIENT, DB, data):
    """
    Insert transformed albums data into the MongoDB database.
    :param MONGODB_CLIENT: the client to connect to the MongoDB database
    :param DB: the name of the database
    :param data: the transformed albums data
    :return: the message indicating the success of the insertion
    """
    logging.info(f"Inserting albums data into {DB}")
    spotifydb = MONGODB_CLIENT[DB]

    albums_collection = spotifydb["albums"]

    # Convert JSON strings back to Python lists/dictionaries for insertion
    albums = json.loads(data)

    # Insert data into collections
    for album in albums:
        if albums_collection.count_documents({"id": album["id"]}, limit=1) == 0:
            albums_collection.insert_one(album)
            logging.info(f"Inserting {album['name']} into albums collection.")
        else:
            logging.info(f"Album {album['name']} already exists in albums collection.")

    logging.info("Inserted transformed albums successfully.")


def insert_artists(MONGODB_CLIENT, DB, data):
    """
    Insert transformed artists data into the MongoDB database.
    :param MONGODB_CLIENT: the client to connect to the MongoDB database
    :param DB: the name of the database
    :param data: the transformed artists data
    :return: the message indicating the success of the insertion
    """
    logging.info(f"Inserting artists data into {DB}")
    spotifydb = MONGODB_CLIENT[DB]

    artists_collection = spotifydb["artists"]

    # Convert JSON strings back to Python lists/dictionaries for insertion
    artists = json.loads(data)

    # Insert data into collections
    for artist in artists:
        if artists_collection.count_documents({"id": artist["id"]}, limit=1) == 0:
            artists_collection.insert_one(artist)
            logging.info(f"Inserting {artist['name']} into artists collection.")
        else:
            logging.info(f"Artist {artist['name']} already exists in artists collection.")

    logging.info("Inserted transformed artists successfully.")


def insert_playlist(MONGODB_CLIENT, DB, data):
    """
    Insert playlist data into the MongoDB database.
    :param MONGODB_CLIENT: the client to connect to the MongoDB database
    :param DB: the name of the database
    :param data: the playlist data
    :return: the message indicating the success of the insertion
    """
    logging.info(f"Inserting playlist data into {DB}")
    spotifydb = MONGODB_CLIENT[DB]

    playlists = spotifydb["playlists"]

    # Convert JSON strings back to Python lists/dictionaries for insertion
    playlist_data = json.loads(data)

    # Insert data into collections or update if exists
    playlists.update_one(
        {"playlist_id": playlist_data["playlist_id"]},
        {"$set": playlist_data},
        upsert=True
    )

    logging.info("Inserted or updated playlist data successfully.")


def insert_recommendation(MONGODB_CLIENT, DB, data):
    """
    Insert recommendation data into the MongoDB database.
    :param MONGODB_CLIENT: the client to connect to the MongoDB database
    :param DB: the name of the database
    :param data: the recommendation data
    :return: the message indicating the success of the insertion
    """
    spotifydb = MONGODB_CLIENT[DB]
    logging.info(f"Inserting recommendation data into the database.")
    recommendations = spotifydb["recommendations"]
    for track in data:
        track_id = track['id']
        recommendations.update_one(
            {"id": track_id},
            {"$set": track},
            upsert=True
        )
    logging.info("Inserted or updated recommendation data successfully.")
