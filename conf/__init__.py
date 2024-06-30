"""
conf/__init__.py

The conf package contains tools that will be used by the backend. Such as Databases (ChromaDB, MongoDB),
Fine Tuning jobs (only done manually in the code and not in the interface), tools to parse, convert and manipulate
json data and most importantly the communication with Spotify API.

In this file, we define the variables that will be used by the tools and the backend.
"""

import openai
from chromadb.utils import embedding_functions
from flask import Flask
import os
from dotenv import load_dotenv
import chromadb
from pymongo import MongoClient

# load environment variables
load_dotenv()

# Define variables needed for Spotify API
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = ('user-read-private user-read-email user-library-read user-top-read playlist-modify-public '
         'playlist-modify-private')
STATE_KEY = 'spotify_auth_state'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

MONGODB_CLIENT = MongoClient("mongodb://localhost:27017/")
DB_NAME = "spotifydb"
COLLECTIONS = ["liked_songs", "albums", "artists", "playlists", "recommendations"]
