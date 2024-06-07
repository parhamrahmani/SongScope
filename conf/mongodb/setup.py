import pymongo
from pymongo import MongoClient
from conf.jsontools.tools import extract_and_transform_tracks
import json


def setup_db(MONGODB_CLIENT, DB):
    # Create a database called "spotifydb"
    MONGODB_CLIENT[DB]


def setup_collections(MONGODB_CLIENT, DB, COLLECTIONS):
    # Access the database called "spotifydb"
    spotifydb = MONGODB_CLIENT[DB]

    # Create collections
    for collection in COLLECTIONS:
        if collection not in spotifydb.list_collection_names():
            spotifydb.create_collection(collection)


def insert_example_tracks(MONGODB_CLIENT, DB, data):
    spotifydb = MONGODB_CLIENT[DB]

    liked_songs = spotifydb["liked_songs"]

    # Convert JSON strings back to Python lists/dictionaries for insertion
    tracks = json.loads(data)

    # Insert data into collections
    for track in tracks:
        if liked_songs.count_documents({"track_id": track["track_id"]}, limit=1) == 0:
            liked_songs.insert_one(track)

    print("Inserted transformed tracks successfully.")


def insert_example_albums(MONGODB_CLIENT, DB, data):
    spotifydb = MONGODB_CLIENT[DB]

    albums_collection = spotifydb["albums"]

    # Convert JSON strings back to Python lists/dictionaries for insertion
    albums = json.loads(data)

    # Insert data into collections
    for album in albums:
        if albums_collection.count_documents({"id": album["id"]}, limit=1) == 0:
            albums_collection.insert_one(album)

    print("Inserted transformed albums successfully.")


def insert_example_artists(MONGODB_CLIENT, DB, data):
    spotifydb = MONGODB_CLIENT[DB]

    artists_collection = spotifydb["artists"]

    # Convert JSON strings back to Python lists/dictionaries for insertion
    artists = json.loads(data)

    # Insert data into collections
    for artist in artists:
        if artists_collection.count_documents({"id": artist["id"]}, limit=1) == 0:
            artists_collection.insert_one(artist)

    print("Inserted transformed artists successfully.")
