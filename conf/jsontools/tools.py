import json

def extract_song_info_into_one_text(song):
    track = song['track']
    album = track['album']

    # get the song id
    song_id = track['id']
    # get the song title
    song_title = track['name']
    # get the artist name
    artist_name = ', '.join([artist['name'].lower().strip() for artist in track['artists']])
    # get the album name
    album_name = album['name']
    # get the release date
    release_date = album['release_date'].split('-')[0]

    output = f"Title: {song_title} Artist: {artist_name} Album: {album_name} Release Date: {release_date}"

    return song_id, output


def extract_and_insert_tracks(data, liked_songs_collection):
    tracks = data.get("tracks", [])
    for track in tracks:
        liked_songs_collection.insert_one(track)
    print("Inserted tracks successfully.")


def extract_and_transform_tracks(data):
    if "tracks" in data:
        tracks = data["tracks"]
    else:
        tracks = [data]

    transformed_tracks = []
    transformed_albums = []
    transformed_artists = []

    for track in tracks:
        # Extract genres from artists
        genres = []
        for artist in track["artists"]:
            # Simulate extracting genres for the example (assuming each artist has a 'genres' field)
            genres.extend(artist.get("genres", []))

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
            "genres": genres
        }
        transformed_tracks.append(track_info)

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

    return tracks_json, albums_json, artists_json
