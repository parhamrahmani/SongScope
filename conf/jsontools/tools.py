def extract_song_info(song):
    track = song['track']
    album = track['album']

    # Extract required fields
    song_info = {
        'id': track['id'],
        'name': track['name'],
        'artist': ', '.join([artist['name'] for artist in track['artists']]),
        'album_title': album['name'],
        'album_year': album['release_date'].split('-')[0],
    }

    return song_info

# push tets