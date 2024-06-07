from pymongo import MongoClient
from conf.mongodb.setup import setup_db, setup_collections, insert_example_tracks, insert_example_albums, insert_example_artists
from conf.jsontools.tools import extract_and_transform_tracks
from conf.jsontools.json_loader import load_data

# Load your data (this function should be implemented to return the JSON data)
data = load_data('example_json_files/example_tracks.json')

# Extract and transform the data
tracks_json, albums_json, artists_json = extract_and_transform_tracks(data)

MONGODB_CLIENT = MongoClient("mongodb://localhost:27017/")
DB_NAME = "spotifydb"
COLLECTIONS = ["liked_songs", "albums", "artists"]

# Setup database and collections
setup_db(MONGODB_CLIENT, DB_NAME)
setup_collections(MONGODB_CLIENT, DB_NAME, COLLECTIONS)

# Insert example data
insert_example_tracks(MONGODB_CLIENT, DB_NAME, tracks_json)
insert_example_albums(MONGODB_CLIENT, DB_NAME, albums_json)
insert_example_artists(MONGODB_CLIENT, DB_NAME, artists_json)

# Second round of data insertion
data = load_data('example_json_files/example_track.json')
track_json, album_json, artist_json = extract_and_transform_tracks(data)

insert_example_tracks(MONGODB_CLIENT, DB_NAME, track_json)
insert_example_albums(MONGODB_CLIENT, DB_NAME, album_json)
insert_example_artists(MONGODB_CLIENT, DB_NAME, artist_json)