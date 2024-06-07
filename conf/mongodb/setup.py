import json


def setup_db(MONGODB_CLIENT, DB):
    print(f"Setting up database {DB}")
    # Create a database called "spotifydb"
    MONGODB_CLIENT[DB]


def setup_collections(MONGODB_CLIENT, DB, COLLECTIONS):
    print(f"Setting up collections in database {DB}")
    # Access the database called "spotifydb"
    spotifydb = MONGODB_CLIENT[DB]

    # Create collections
    for collection in COLLECTIONS:
        if collection not in spotifydb.list_collection_names():
            spotifydb.create_collection(collection)
            print(f"Created collection: {collection}")

