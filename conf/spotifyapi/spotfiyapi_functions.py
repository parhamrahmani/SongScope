from pymongo import MongoClient
import conf.spotifyapi.spotifyauth
from backend.application import app
from flask import redirect, request, session, Response, jsonify
from datetime import datetime
import requests
import json
import random
from conf.jsontools.tools import *
from conf.jsontools.json_loader import load_data
from conf.mongodb.setup import *
from conf.jsontools.tools import *
from conf.mongodb.insertion import *
from backend.generate_data import generate_seed_tracks

MONGODB_CLIENT = MongoClient("mongodb://localhost:27017/")
DB_NAME = "spotifydb"


@app.route("/playlists")
def get_playlists():
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
def get_liked_songs(return_data=False):
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

    data = load_data('example_json_files/temp.json')
    liked_songs_json = extract_and_transform_liked_songs(data)
    tracks_json, albums_json, artists_json = extract_and_transform_tracks(liked_songs_json)
    insert_tracks(MONGODB_CLIENT, DB_NAME, tracks_json)
    insert_albums(MONGODB_CLIENT, DB_NAME, albums_json)
    insert_artists(MONGODB_CLIENT, DB_NAME, artists_json)

    return all_tracks


@app.route("/top_tracks")
def get_top_tracks():
    if 'access_token' not in session:
        return redirect('/login')
    if datetime.now().timestamp() > session.get('expires_at', 0):
        return redirect('/refresh_token')

    headers = {
        'Authorization': f'Bearer {session["access_token"]}'
    }

    response = requests.get(f"{API_BASE_URL}me/top/tracks?time_range=long_term&limit=20", headers=headers)
    if response.status_code == 200:
        return Response(response.content, mimetype='application/json')
    else:
        return Response(json.dumps({'error': 'Failed to fetch top tracks', 'status': response.status_code}),
                        status=response.status_code, mimetype='application/json')


API_BASE_URL = 'https://api.spotify.com/v1/'


@app.route("/recommendations", methods=['GET'])
def get_recommendations():
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
                        mimetype='application/json')
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
    print(f"Parameters received: {params}")
    # Construct the request URL
    url = f"{API_BASE_URL}recommendations"
    print(f"Request URL: {url}")
    print(f"Request Params: {params}")
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
        return Response(json.dumps(enriched_data), mimetype='application/json')
    else:
        print(f"Error from Spotify API: {recommendations_response.content}")
        return Response(recommendations_response.content, status=recommendations_response.status_code,
                        mimetype='application/json')


@app.route("/create_playlist", methods=['POST'])
def create_playlist():
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
                        mimetype='application/json')

    user_profile_data = user_profile_response.json()
    user_id = user_profile_data['id']

    # Create a new playlist
    playlist_name = f"SongScope generated playlist #{random.randint(1000, 9999)}"
    create_playlist_response = requests.post(
        f"{API_BASE_URL}users/{user_id}/playlists",
        headers={
            'Authorization': f'Bearer {session["access_token"]}',
            'Content-Type': 'application/json'
        },
        json={
            'name': playlist_name,
            'description': 'A playlist generated by SongScope',
            'public': False
        }
    )

    if create_playlist_response.status_code != 201:
        return Response(create_playlist_response.content, status=create_playlist_response.status_code,
                        mimetype='application/json')

    playlist_data = create_playlist_response.json()
    playlist_id = playlist_data['id']

    # Add tracks to the new playlist
    tracks = request.json.get('tracks', [])
    track_uris = [track['uri'] for track in tracks]

    add_tracks_response = requests.post(
        f"{API_BASE_URL}playlists/{playlist_id}/tracks",
        headers={
            'Authorization': f'Bearer {session["access_token"]}',
            'Content-Type': 'application/json'
        },
        json={'uris': track_uris}
    )

    if add_tracks_response.status_code != 201:
        return Response(add_tracks_response.content, status=add_tracks_response.status_code,
                        mimetype='application/json')

    return jsonify({'message': 'Playlist created successfully', 'playlist_id': playlist_id})


@app.route("/generate_random_recommendations/<int:num_recommendations>", methods=['GET'])
def generate_random_recommendations(num_recommendations):
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
        print(f"Parameters received: {params}")
        # Construct the request URL
        url = f"{API_BASE_URL}recommendations"
        print(f"Request URL: {url}")
        print(f"Request Params: {params}")
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
            print(f"Error from Spotify API: {recommendations_response.content}")
            return Response(recommendations_response.content, status=recommendations_response.status_code,
                            mimetype='application/json')
    return jsonify(all_recommendations)