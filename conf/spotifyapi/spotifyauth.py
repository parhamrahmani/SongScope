"""
conf/spotifyapi/spotifyauth.py

Handles the authentication process for the Spotify API.
"""
import os
from datetime import datetime
from urllib.parse import urlencode
import requests
from flask import request, redirect, session, jsonify
from conf import *
import conf.spotifyapi.spotfiyapi_functions
import openai
import conf.spotifyapi.spotifyauth
from flask import Flask, request, redirect, session
from backend.welcome_auth import app



@app.route('/check_auth')
def check_auth():
    if 'access_token' in session:
        print("Access token exists in session")
        print("Access token: ", session['access_token'])
        return True
    print("Access token does not exist in session")
    return False


@app.route('/login')
def login():
    # define query params
    query_params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'scope': SCOPE,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': 'true'
    }

    auth_url = f"{AUTH_URL}?{urlencode(query_params)}"
    return redirect(auth_url)


@app.route('/callback')
def callback():
    # check for errors in query params
    if 'error' in request.args:
        return 'Error: ' + request.args['error']

    # Proceed if we have the authorization code form spotify
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET
        }
        print("Callback request body: ", req_body)
        response = requests.post(TOKEN_URL, data=req_body)

        # check if the request was successful
        if response.status_code != 200:
            return f"Failed to get token: {response.text}", response.status_code
        # if successful, store the token in the session
        token_info = response.json()
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info.get('expires_in', 3600)  # default to 1 hour

        os.environ['SPOTIFY_ACCESS_TOKEN'] = session['access_token']
        os.environ['SPOTIFY_REFRESH_TOKEN'] = session['refresh_token']
        os.environ['SPOTIFY_EXPIRES_AT'] = str(session['expires_at'])



        return redirect('/interface')

    return 'Error: No code in request'


@app.route("/refresh_token")
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        os.environ['SPOTIFY_ACCESS_TOKEN'] = session['access_token']
        os.environ['SPOTIFY_EXPIRES_AT'] = str(session['expires_at'])

        return redirect('/chat')
