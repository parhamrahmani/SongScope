import os

import chromadb

CHROMADB_PATH = os.path.abspath(os.getenv('CHROMADB_PATH'))
client = chromadb.PersistentClient(path=CHROMADB_PATH)
client.heartbeat()  # returns a nanosecond heartbeat. Useful for making sure the client remains connected.

# create or get the collections
liked_songs_collection = client.get_or_create_collection(name="liked_songs", )
recommendations_collection = client.get_or_create_collection(name="recommendations", )

# Add the song to the liked songs collection
def add_to_liked_songs(song_id, song_info):
    try:

        liked_songs_collection.add(
            documents=[song_info],
            ids=[song_id]
        )
        print(f"Added song to liked songs collection: liked_songs")
        print(f"Song ID: {song_id}  \nSong Info: {song_info}")
        count = liked_songs_collection.count()
        print(f"Total songs in liked songs collection: {count}")
    except Exception as e:
        print(f"Error adding song to liked songs collection: {e}")


# peak into the liked songs collection
def query_liked_songs(query_text, number_of_results):
    try:
        # Query the liked songs collection
        results = liked_songs_collection.query(
            query_texts=query_text,
            n_results=number_of_results
        )

        # Extract relevant data
        ids = results.get('ids', [[]])[0]
        documents = results.get('documents', [[]])[0]

        # Format and print the results as id: item
        formatted_results = [f"{id}: {document}" for id, document in zip(ids, documents)]
        for result in formatted_results:
            print(result)

        # Optionally, return the formatted results
        return formatted_results

    except Exception as e:
        print(f"Error querying the liked songs collection: {e}")
        return []





