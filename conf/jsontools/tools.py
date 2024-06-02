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
