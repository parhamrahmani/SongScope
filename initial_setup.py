"""
This will initialize the Project, there are also more prerequisites to be done before running this script.

0. Read the Spotify API documentation: https://developer.spotify.com/documentation/web-api/
to create an application there and get the client_id and client_secret and also set the addresses and callback URIs.
Otherwise nothing will work.

1. in your .env file, add the following variables:
    - SPOTIFY_CLIENT_ID -> get from Spotify Developer Dashboard
    - SPOTIFY_CLIENT_SECRET -> get from Spotify Developer Dashboard
    - REDIRECT_URI -> where you call the callback function, e.g. http://localhost:5000/callback
    - OPENAI_API_KEY -> get from OpenAI API Dashboard
    - OPENAI_CLIENT -> use the OPENAI_API_KEY to create a client
    - AI_MODEL -> the model you want to use, e.g. "gpt-3.5-turbo"
    - OPEN_AI_ASSISTANT_ID -> get from OpenAI API Dashboard
    - MONGODB_URI -> the URI to your MongoDB database, e.g. "mongodb://localhost:27017/"
    - CHROMADB_PATH -> the path to your ChromaDB database, e.g. "data"
    - FLASK_SECRET_KEY -> a secret key for Flask, e.g. "my_secret" you can set this as anything. remember to keep it
    secret.
    - TAVILY_KEY -> get from Tavily API Dashboard

2. Make sure you have the required libraries installed:
    - pymongo -> MongoDB Python driver
    - openai -> OpenAI Python client
    - chroma -> ChromaDB Python client
    - flask -> Flask web framework
    - requests -> HTTP requests library
    - python-dotenv -> Python dotenv library to load environment variables
    - chainlit -> Chainlit Python client


"""

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

# Load your data
data = load_json('data/examples/example_tracks.json')

# Extract and transform the data
tracks_json, albums_json, artists_json = extract_and_transform_tracks(data)

MONGODB_CLIENT = MongoClient("mongodb://localhost:27017/")
DB_NAME = "spotifydb"
COLLECTIONS = ["liked_songs", "albums", "artists", "playlists", "recommendations"]

# Setup database and collections
setup_db(MONGODB_CLIENT, DB_NAME)
setup_collections(MONGODB_CLIENT, DB_NAME, COLLECTIONS)
print(
    "Initial Database setup completed. Created database 'spotifydb' and collections 'liked_songs', 'albums', 'artists', 'playlists', 'recommendations'.")

# Insert example data
print("Inserting example data... Track Data")
insert_tracks(MONGODB_CLIENT, DB_NAME, tracks_json)
insert_albums(MONGODB_CLIENT, DB_NAME, albums_json)
insert_artists(MONGODB_CLIENT, DB_NAME, artists_json)
print("First round of data insertion completed.")

print("Second round of data insertion... Playlist data")
data = load_json('data/examples/example_playlist.json')
playlist_json = extract_and_transform_playlists(data)
insert_playlist(MONGODB_CLIENT, DB_NAME, playlist_json)
print("Second round of data insertion completed.")

print("Third round of data insertion... Liked Songs data")
data = load_json('data/examples/example_liked_tracks.json')
liked_songs_json = extract_and_transform_liked_songs(data)
tracks_json, albums_json, artists_json = extract_and_transform_tracks(liked_songs_json)
insert_tracks(MONGODB_CLIENT, DB_NAME, tracks_json)
insert_albums(MONGODB_CLIENT, DB_NAME, albums_json)
insert_artists(MONGODB_CLIENT, DB_NAME, artists_json)
print("Third round of data insertion completed.")



