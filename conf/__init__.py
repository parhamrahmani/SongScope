from flask import Flask
import os
from dotenv import load_dotenv
import chromadb
from pymongo import MongoClient

# load environment variables
load_dotenv()

# Define variables
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = ('user-read-private user-read-email user-library-read user-top-read playlist-modify-public '
         'playlist-modify-private')

STATE_KEY = 'spotify_auth_state'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

# OPENAI Variables
OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')
OPEN_AI_ASSISTANT_ID = os.getenv('OPEN_AI_ASSISTANT_ID')
AI_MODEL = os.getenv('AI_MODEL')
CHROMA_DB_PATH = os.getenv('CHROMADB_PATH')

MONGODB_CLIENT = MongoClient("mongodb://localhost:27017/")
DB_NAME = "spotifydb"
COLLECTIONS = ["liked_songs", "albums", "artists", "playlists", "recommendations"]