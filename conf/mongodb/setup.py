"""
conf/mongodb/setup.py

This module contains functions to setup the MongoDB database and collections for before using the program for the first
 time.
"""

import json
import logging


def setup_db(MONGODB_CLIENT, DB):
    """
    Setup the MongoDB database.
    :param MONGODB_CLIENT:  the client to connect to the MongoDB database
    :param DB: the name of the database
    :return: the message indicating the success of the setup
    """
    logging.info(f"Setting up database {DB}")
    # Create a database called "spotifydb"
    MONGODB_CLIENT[DB]


def setup_collections(MONGODB_CLIENT, DB, COLLECTIONS):
    """
    Setup the collections in the MongoDB database.
    :param MONGODB_CLIENT: the client to connect to the MongoDB database
    :param DB: the name of the database
    :param COLLECTIONS: the list of collections to create
    :return: the message indicating the success of the setup
    """
    print(f"Setting up collections in database {DB}")
    # Access the database called "spotifydb"
    spotifydb = MONGODB_CLIENT[DB]

    # Create collections
    for collection in COLLECTIONS:
        if collection not in spotifydb.list_collection_names():
            spotifydb.create_collection(collection)
            print(f"Created collection: {collection}")

