"""
conf/spotifyapi/spotifyapi_functions.py

Handles the Spotify API functions.
"""
import logging
import os

import urllib.parse
import re

import urllib.parse
from pymongo import MongoClient
from backend.welcome_auth import app
from flask import redirect, request, session, Response, jsonify
from datetime import datetime
import requests
import random
from conf.jsontools.tools import load_json
from conf.jsontools.tools import *
from conf.mongodb.insertion import *
from conf.finetuning.generate_data import generate_seed_tracks

MONGODB_CLIENT = MongoClient("mongodb://localhost:27017/")
DB_NAME = "spotifydb"


@app.route("/playlists")
def get_playlists():
    """
    Get the user's playlists.
    :return: the user's playlists
    """
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh_token')

    headers = {
        'Authorization': f'Bearer {session["access_token"]}'

    }
    response = requests.get(f"{API_BASE_URL}me/playlists", headers=headers)

    return response.json()


@app.route("/liked_songs")
def get_liked_songs():
    """
    Get the user's liked songs.

    :return: the user's liked songs
    """
    if 'access_token' not in session:
        return redirect('/login')

    access_token = session['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    all_tracks = []
    url = f"{API_BASE_URL}me/tracks?limit=20"

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            app.logger.error(f"Failed to fetch data: {response.text}")
            return f"Failed to fetch data: {response.text}", response.status_code

        data = response.json()
        all_tracks.extend(data.get('items'))
        url = data.get('next')

    # put the data into a temp json file
    with open('example_json_files/temp.json', 'w') as file:
        json.dump(all_tracks, file)

    data = load_json('example_json_files/temp.json')
    liked_songs_json = extract_and_transform_liked_songs(data)
    tracks_json, albums_json, artists_json = extract_and_transform_tracks(liked_songs_json)
    insert_tracks(MONGODB_CLIENT, DB_NAME, tracks_json)
    insert_albums(MONGODB_CLIENT, DB_NAME, albums_json)
    insert_artists(MONGODB_CLIENT, DB_NAME, artists_json)

    return all_tracks


@app.route("/top_tracks")
def get_top_tracks():
    """
    Get the user's top tracks.
    :return: the user's top tracks
    """
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session.get('expires_at', 0):
        return redirect('/refresh_token')

    headers = {
        'Authorization': f'Bearer {session["access_token"]}'
    }

    response = requests.get(f"{API_BASE_URL}me/top/tracks?time_range=long_term&limit=20", headers=headers)
    if response.status_code == 200:
        return Response(response.content, mimetype='backend/json')
    else:
        return Response(json.dumps({'error': 'Failed to fetch top tracks', 'status': response.status_code}),
                        status=response.status_code, mimetype='backend/json')


API_BASE_URL = 'https://api.spotify.com/v1/'


@app.route("/recommendations", methods=['GET'])
def get_recommendations():
    """
    Get recommendations based on the user's top tracks.
    :return: the recommendations based on the user's top tracks
    """
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session.get('expires_at', 0):
        return redirect('/refresh_token')
    headers = {
        'Authorization': f'Bearer {session["access_token"]}'
    }
    # Retrieve top tracks to use as seeds
    top_tracks_response = requests.get(f"{API_BASE_URL}me/top/tracks?limit=5&time_range=short_term", headers=headers)
    if top_tracks_response.status_code != 200:
        return Response(top_tracks_response.content, status=top_tracks_response.status_code,
                        mimetype='backend/json')
    top_tracks_data = top_tracks_response.json()
    seed_tracks = ','.join([track['id'] for track in top_tracks_data['items']])
    # Get parameters from the request in webpage form
    min_energy = float(request.args.get('min_energy', 0.4))
    max_energy = float(request.args.get('max_energy', 0.8))
    target_popularity = int(request.args.get('target_popularity', random.randint(1, 100)))
    target_acousticness = float(request.args.get('target_acousticness', 0.5))
    target_instrumentalness = float(request.args.get('target_instrumentalness', 0.5))
    target_tempo = float(request.args.get('target_tempo', 120))
    # Define additional parameters for recommendations, if necessary
    params = {
        'seed_tracks': seed_tracks,
        'limit': 20,
        'market': 'US',
        'min_energy': min_energy,
        'max_energy': max_energy,
        'target_popularity': target_popularity,
        'target_acousticness': target_acousticness,
        'target_instrumentalness': target_instrumentalness,
        'target_tempo': target_tempo
    }
    # Remove empty parameters
    params = {k: v for k, v in params.items() if v}
    # Debugging logs
    logging.info(f"Parameters received: {params}")
    # Construct the request URL
    url = f"{API_BASE_URL}recommendations"
    logging.info(f"Request URL: {url}")
    logging.info(f"Request Params: {params}")
    # Fetch recommendations based on the seeds
    recommendations_response = requests.get(
        url,
        headers={'Authorization': f'Bearer {session["access_token"]}'},
        params=params
    )
    if recommendations_response.status_code == 200:
        recommendations_data = recommendations_response.json()
        enriched_data = extract_recommendations_with_weights(recommendations_data, params)
        insert_recommendation(MONGODB_CLIENT, DB_NAME, enriched_data)
        return Response(json.dumps(enriched_data), mimetype='backend/json')
    else:
        logging.error(f"Error from Spotify API: {recommendations_response.content}")
        return Response(recommendations_response.content, status=recommendations_response.status_code,
                        mimetype='backend/json')


@app.route("/create_playlist", methods=['POST'])
def create_playlist():
    """
    Create a new playlist and add tracks to it.
    :return: the response message
    """
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session.get('expires_at', 0):
        return redirect('/refresh_token')

    # Get the current user's profile to retrieve the user ID
    user_profile_response = requests.get(
        f"{API_BASE_URL}me",
        headers={'Authorization': f'Bearer {session["access_token"]}'}
    )

    if user_profile_response.status_code != 200:
        return Response(user_profile_response.content, status=user_profile_response.status_code,
                        mimetype='backend/json')

    user_profile_data = user_profile_response.json()
    user_id = user_profile_data['id']

    # Create a new playlist
    playlist_name = f"SongScope generated playlist #{random.randint(1000, 9999)}"
    create_playlist_response = requests.post(
        f"{API_BASE_URL}users/{user_id}/playlists",
        headers={
            'Authorization': f'Bearer {session["access_token"]}',
            'Content-Type': 'backend/json'
        },
        json={
            'name': playlist_name,
            'description': 'A playlist generated by SongScope',
            'public': False
        }
    )

    if create_playlist_response.status_code != 201:
        return Response(create_playlist_response.content, status=create_playlist_response.status_code,
                        mimetype='backend/json')

    playlist_data = create_playlist_response.json()
    playlist_id = playlist_data['id']

    # Add tracks to the new playlist
    tracks = request.json.get('tracks', [])
    track_uris = [track['uri'] for track in tracks]

    add_tracks_response = requests.post(
        f"{API_BASE_URL}playlists/{playlist_id}/tracks",
        headers={
            'Authorization': f'Bearer {session["access_token"]}',
            'Content-Type': 'backend/json'
        },
        json={'uris': track_uris}
    )

    if add_tracks_response.status_code != 201:
        return Response(add_tracks_response.content, status=add_tracks_response.status_code,
                        mimetype='backend/json')

    return jsonify({'message': 'Playlist created successfully', 'playlist_id': playlist_id})


@app.route("/generate_random_recommendations/<int:num_recommendations>", methods=['GET'])
def generate_random_recommendations(num_recommendations):
    """
    Generate random recommendations based on seed tracks and weights. Used for fine-tuning and training.
    :param num_recommendations: the number of recommendations to generate
    :return: the generated recommendations
    """
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session.get('expires_at', 0):
        return redirect('/refresh_token')
    headers = {
        'Authorization': f'Bearer {session["access_token"]}'
    }

    all_recommendations = []
    for _ in range(num_recommendations):
        # retrieve random seed tracks
        seed_tracks = generate_seed_tracks(MONGODB_CLIENT, DB_NAME)
        # Get parameters from the request in webpage form
        min_energy = random.uniform(0.1, 0.9)  # Adjusted range
        max_energy = random.uniform(min_energy, 1.0)
        target_popularity = random.randint(1, 100)
        target_acousticness = random.uniform(0.1, 0.9)  # Adjusted range
        target_instrumentalness = random.uniform(0.1, 0.9)  # Adjusted range
        target_tempo = random.uniform(60, 180)
        # Define additional parameters for recommendations, if necessary
        params = {
            'seed_tracks': seed_tracks,
            'limit': 20,
            'market': 'US',
            'min_energy': min_energy,
            'max_energy': max_energy,
            'target_popularity': target_popularity,
            'target_acousticness': target_acousticness,
            'target_instrumentalness': target_instrumentalness,
            'target_tempo': target_tempo
        }
        # Remove empty parameters
        params = {k: v for k, v in params.items() if v}
        # Debugging logs
        logging.info(f"Parameters received: {params}")
        # Construct the request URL
        url = f"{API_BASE_URL}recommendations"
        logging.info(f"Request URL: {url}")
        logging.info(f"Request Params: {params}")
        # Fetch recommendations based on the seeds
        recommendations_response = requests.get(
            url,
            headers={'Authorization': f'Bearer {session["access_token"]}'},
            params=params
        )
        if recommendations_response.status_code == 200:
            recommendations_data = recommendations_response.json()
            enriched_data = extract_recommendations_with_weights(recommendations_data, params)
            insert_recommendation(MONGODB_CLIENT, DB_NAME, enriched_data)
            all_recommendations.append(enriched_data)
        else:
            logging.info(f"Error from Spotify API: {recommendations_response.content}")
            return Response(recommendations_response.content, status=recommendations_response.status_code,
                            mimetype='backend/json')
    return jsonify(all_recommendations)


def search_track_on_spotify(track_name, artist_name):
    """
    Search for a track on Spotify. Used for result verification in Chatbot.
    :param track_name
    :param artist_name
    :return: the search result
    """
    logging.info(f"Searching Spotify for track: {track_name} by {artist_name}")
    access_token = session.get('access_token')
    if not access_token:
        access_token = os.environ.get('SPOTIFY_ACCESS_TOKEN')
        if not access_token:
            return f"(No Spotify access token available)"

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Construct the query with double encoding
    track_name_encoded = urllib.parse.quote(track_name)
    artist_name_encoded = urllib.parse.quote(artist_name)
    query = f"track%3A{track_name_encoded}%2520artist%3A{artist_name_encoded}"
    logging.info(f"Constructed query: {query}")

    params = {
        'q': query,
        'type': 'track',
        'limit': 20  # Increase limit to fetch more results
    }

    try:
        url = f"https://api.spotify.com/v1/search?{urllib.parse.urlencode(params)}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        total_results = len(data['tracks']['items']) if 'tracks' in data and 'items' in data['tracks'] else 0
        logging.info(f"Total results found: {total_results}")

        if total_results > 0:
            found_tracks = []
            for track in data['tracks']['items']:
                track_name_match = track_name.lower() in track['name'].lower()
                artist_name_match = any(artist_name.lower() in artist['name'].lower() for artist in track['artists'])

                logging.info(f"Result: {track['name']} by {track['artists'][0]['name']}")
                if track_name_match and artist_name_match:
                    logging.info(f"Found track: {track['name']} by {track['artists'][0]['name']}")
                    spotify_url = track['external_urls'].get('spotify', 'No Spotify URL available')
                    found_tracks.append(f"{track['name']} by {track['artists'][0]['name']} - {spotify_url}")
                    break

            if found_tracks:
                return "\n".join(found_tracks)
            else:
                logging.info(f"Track not found: {track_name} by {artist_name}")
                return f"({track_name} by {artist_name} - Not found on Spotify)"
        else:
            logging.info(f"Track not found: {track_name} by {artist_name}")
            return f"({track_name} by {artist_name} - Not found on Spotify)"
    except requests.RequestException as e:
        logging.error(f"Error searching Spotify: {str(e)}")
        return f"({track_name} by {artist_name} - Error searching Spotify)"
