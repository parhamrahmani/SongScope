import chromadb
from chromadb.utils import embedding_functions

# Configure Chroma DB client to save and load from your local machine
client = chromadb.PersistentClient(path="db")

# Standard embedding function
default_ef = embedding_functions.DefaultEmbeddingFunction()

# Create or get a collection with the default embedding function
liked_songs_collection = client.get_or_create_collection(name="liked_songs_collection", embedding_function=default_ef)

""""
# Add a sample song to the collection
def add_sample_song():
    sample_song_text = "Sample Song by Sample Artist"
    sample_song_metadata = {
        'id': 'sample_id',
        'name': 'Sample Song',
        'artist': 'Sample Artist',
        'album_title': 'Sample Album',
        'album_year': '2023'
    }

    liked_songs_collection.add(
        documents=[sample_song_text],  # Text of the song for embedding
        metadatas=[sample_song_metadata],  # Metadata of the song
        ids=[sample_song_metadata['id']]  # Unique ID for the song
    )

# Function to query the collection
def query_collection():
    results = liked_songs_collection.query(
        query_texts=["Sample Song by Sample Artist"],
        n_results=1
    )
    print(results)


# Add sample song to the collection
print("Adding sample song to the collection...")
add_sample_song()

# Query the collection
print("Querying the collection for the sample song...")
query_collection()
"""