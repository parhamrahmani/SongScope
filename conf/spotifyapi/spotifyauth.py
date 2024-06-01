from datetime import datetime
from urllib.parse import urlencode
import requests
from flask import request, redirect, session
from conf import *


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

        return redirect('/home')

    return 'Error: No code in request'
