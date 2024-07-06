"""
conf/mongodb/query.py

This module contains functions to query MongoDB collections by specific fields or fetch all documents.

"""
import logging

from pymongo import MongoClient
import json
from conf.jsontools.tools import convert_documents_to_json


# Function to query documents by specific fields
def collection_query_by_fields(MONGODB_CLIENT, DB_NAME, COLLECTION, INPUT_DICT):
    """
    Query the MongoDB collection by specific fields.
    :param MONGODB_CLIENT: the client to connect to the MongoDB database
    :param DB_NAME: the name of the database
    :param COLLECTION: the name of the collection
    :param INPUT_DICT: the dictionary containing the fields to query
    :return: the documents that match the query
    """
    db = MONGODB_CLIENT[DB_NAME]
    col = db[COLLECTION]
    # Use the INPUT_DICT directly in the find method
    doc = col.find(INPUT_DICT)
    return doc


def collection_query_all(MONGODB_CLIENT, DB_NAME, COLLECTION):
    """
    Fetch all documents from the MongoDB collection.
    :param MONGODB_CLIENT: the client to connect to the MongoDB database
    :param DB_NAME: the name of the database
    :param COLLECTION: the name of the collection
    :return: the documents in the collection
    """
    db = MONGODB_CLIENT[DB_NAME]
    col = db[COLLECTION]
    total_documents = col.count_documents({})
    logging.info(f"Total documents to fetch: {total_documents}")

    cursor = col.find()
    documents = list(cursor)  # Directly convert cursor to a list
    jsonified_documents = convert_documents_to_json(documents)

    return jsonified_documents
