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
from conf.jsontools.json_loader import load_data
from conf.misc.parsing import extract_weights_from_url

# Load your data
data = load_data('example_json_files/example_tracks.json')

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
data = load_data('example_json_files/example_playlist.json')
playlist_json = extract_and_transform_playlists(data)
insert_playlist(MONGODB_CLIENT, DB_NAME, playlist_json)
print("Second round of data insertion completed.")

print("Third round of data insertion... Liked Songs data")
data = load_data('example_json_files/example_liked_tracks.json')
liked_songs_json = extract_and_transform_liked_songs(data)
tracks_json, albums_json, artists_json = extract_and_transform_tracks(liked_songs_json)
insert_tracks(MONGODB_CLIENT, DB_NAME, tracks_json)
insert_albums(MONGODB_CLIENT, DB_NAME, albums_json)
insert_artists(MONGODB_CLIENT, DB_NAME, artists_json)
print("Third round of data insertion completed.")

# exmaple query


