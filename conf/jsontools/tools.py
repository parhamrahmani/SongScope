import json
import logging


def extract_and_transform_liked_songs(data):
    """
    Extract and transform the liked songs data into a more readable format to save in the collection in MongoDB.
    :param data:  the data to extract and transform
    :return:    the transformed data
    """
    logging.info("Starting to extract and transform liked songs data.")
    if isinstance(data, list):
        items = data
    else:
        items = data.get("items", [])

    liked_songs = []

    for item in items:
        track = item.get("track", {})
        album = track.get("album", {})

        track_info = {
            "album": {
                "album_type": album.get("album_type", ""),
                "total_tracks": album.get("total_tracks", 0),
                "available_markets": album.get("available_markets", []),
                "external_urls": album.get("external_urls", {}),
                "href": album.get("href", ""),
                "id": album.get("id", ""),
                "images": album.get("images", []),
                "name": album.get("name", ""),
                "release_date": album.get("release_date", ""),
                "release_date_precision": album.get("release_date_precision", ""),
                "type": album.get("type", ""),
                "uri": album.get("uri", ""),
                "artists": [
                    {
                        "external_urls": artist.get("external_urls", {}),
                        "href": artist.get("href", ""),
                        "id": artist.get("id", ""),
                        "name": artist.get("name", ""),
                        "type": artist.get("type", ""),
                        "uri": artist.get("uri", "")
                    } for artist in album.get("artists", [])
                ]
            },
            "artists": [
                {
                    "external_urls": artist.get("external_urls", {}),
                    "href": artist.get("href", ""),
                    "id": artist.get("id", ""),
                    "name": artist.get("name", ""),
                    "type": artist.get("type", ""),
                    "uri": artist.get("uri", "")
                } for artist in track.get("artists", [])
            ],
            "available_markets": track.get("available_markets", []),
            "disc_number": track.get("disc_number", 0),
            "duration_ms": track.get("duration_ms", 0),
            "explicit": track.get("explicit", False),
            "external_ids": track.get("external_ids", {}),
            "external_urls": track.get("external_urls", {}),
            "href": track.get("href", ""),
            "id": track.get("id", ""),
            "name": track.get("name", ""),
            "popularity": track.get("popularity", 0),
            "preview_url": track.get("preview_url", ""),
            "track_number": track.get("track_number", 0),
            "type": track.get("type", ""),
            "uri": track.get("uri", ""),
            "is_local": track.get("is_local", False)
        }
        liked_songs.append(track_info)

    logging.info(f"Extracted and transformed {len(liked_songs)} liked songs.")
    return liked_songs


def extract_and_transform_tracks(data):
    """
    Extract and transform the tracks data into a more readable format.
    :param data: the data to extract and transform
    :return: the transformed data
    """
    logging.info("Starting to extract and transform tracks data.")
    tracks_data = data if isinstance(data, list) else data.get("items", [])

    transformed_tracks = []
    transformed_albums = []
    transformed_artists = []

    for item in tracks_data:
        track = item.get("track", item)  # Handle both track objects directly and items containing track objects

        # Extract track information
        track_info = {
            "album_name": track["album"]["name"],
            "artist_name": [artist["name"] for artist in track["artists"]],
            "duration_ms": track["duration_ms"],
            "external_urls": track["external_urls"],
            "href": track["href"],
            "track_id": track["id"],
            "name": track["name"],
            "type": track["type"],
            "uri": track["uri"],
            "release_date": track["album"]["release_date"],
            "popularity": track.get("popularity", 0),
        }
        transformed_tracks.append(track_info)

        print(f"Processed track: {track_info['name']}")

        # Extract album information
        album_info = {
            "id": track["album"]["id"],
            "album_type": track["album"]["album_type"],
            "total_tracks": track["album"]["total_tracks"],
            "external_urls": track["album"]["external_urls"],
            "name": track["album"]["name"],
            "release_date": track["album"]["release_date"],
            "type": track["album"]["type"],
            "uri": track["album"]["uri"],
            "artist_names": [artist["name"] for artist in track["album"]["artists"]]
        }
        if album_info not in transformed_albums:
            transformed_albums.append(album_info)

        # Extract artist information
        for artist in track["artists"]:
            artist_info = {
                "name": artist["name"],
                "type": artist["type"],
                "popularity": artist.get("popularity", 0),
                "id": artist["id"]
            }
            if artist_info not in transformed_artists:
                transformed_artists.append(artist_info)

    # Convert to JSON strings
    tracks_json = json.dumps(transformed_tracks, indent=4)
    albums_json = json.dumps(transformed_albums, indent=4)
    artists_json = json.dumps(transformed_artists, indent=4)

    logging.info(
        f"Extracted and transformed {len(transformed_tracks)} tracks, {len(transformed_albums)} albums, and {len(transformed_artists)} artists.")
    return tracks_json, albums_json, artists_json


def extract_and_transform_playlists(data):
    logging.info("Starting to extract and transform playlists data.")
    playlist_info = {
        "description": data.get("description", ""),
        "playlist_id": data.get("id", ""),
        "external_urls": data.get("external_urls", {}),
        "href": data.get("href", ""),
        "owner": data.get("owner", {}).get("display_name", ""),
        "tracks": []
    }

    for item in data.get("tracks", {}).get("items", []):
        track = item.get("track", {})
        album = track.get("album", {})

        track_info = {
            "track_name": track.get("name", ""),
            "track_id": track.get("id", ""),
            "album": {
                "name": album.get("name", ""),
                "release_date": album.get("release_date", ""),
                "uri": album.get("uri", "")
            },
            "uri": track.get("uri", "")
        }
        playlist_info["tracks"].append(track_info)

    logging.info(f"Extracted and transformed {len(playlist_info['tracks'])} tracks in playlist.")
    # Convert to JSON string
    playlist_json = json.dumps(playlist_info, indent=4)

    return playlist_json


def extract_recommendations_with_weights(recommendations_data, weights):
    """
    Extract recommendations data and enrich it with weights.
    :param recommendations_data:  the recommendations data to extract
    :param weights: the weights to add to each track
    :return: the enriched tracks
    """
    enriched_tracks = []
    for track in recommendations_data['tracks']:
        enriched_track = {
            "album": track["album"]["name"],
            "artists": [artist["name"] for artist in track["artists"]],
            "duration_ms": track["duration_ms"],
            "external_urls": track["external_urls"],
            "href": track["href"],
            "id": track["id"],
            "name": track["name"],
            "popularity": track["popularity"],
            "preview_url": track["preview_url"],
            "uri": track["uri"],
            "disc_number": track.get("disc_number", 0),
            "explicit": track.get("explicit", False),
            "external_ids": track.get("external_ids", {}),
            "is_local": track.get("is_local", False),
            "is_playable": track.get("is_playable", True)
        }
        enriched_track.update(weights)  # Add each weight as a separate field in the track info
        enriched_tracks.append(enriched_track)
    return enriched_tracks


def convert_documents_to_json(documents):
    """
    Convert documents to JSON strings.
    :param documents:  the documents to convert
    :return: the JSON strings
    """
    # Convert each document to JSON
    readable_documents = [json.dumps(doc, default=str) for doc in documents]
    return readable_documents


def load_json(json_path):
    """
    Load JSON data from a file.
    :param json_path: the path to the JSON file
    :return: the loaded JSON data
    """
    # Load your data from a file or any other source
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data
