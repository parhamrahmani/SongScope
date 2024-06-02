from flask import Flask
import os
from dotenv import load_dotenv

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.debug = True

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
