from conf.chromadb import *


# add to liked_songs_collection
def add_to_liked_songs(formatted_songs):
    doc_list = []
    metadata_list = []
    id_list = []

    # Add songs to Chroma DB if they do not already exist
    for song in formatted_songs:
        song_id = song['id']
        song_text = f"{song['name']} by {song['artist']}"
        metadata = {
            'id': song_id,
            'name': song['name'],
            'artist': song['artist'],
            'album_title': song['album_title'],
            'album_year': song['album_year'],
        }

        # Add songs to lists
        doc_list.append(song_text)
        metadata_list.append(metadata)
        id_list.append(song_id)

        if doc_list:
            liked_songs_collection.add(
                documents=doc_list,
                metadatas=metadata_list,
                ids=id_list
            )


