from pymongo import MongoClient
import json
from conf.jsontools.tools import convert_documents_to_json
# Function to query documents by specific fields
def collection_query_by_fields(MONGODB_CLIENT, DB_NAME, COLLECTION, INPUT_DICT):
    db = MONGODB_CLIENT[DB_NAME]
    col = db[COLLECTION]
    # Use the INPUT_DICT directly in the find method
    doc = col.find(INPUT_DICT)
    return doc


def collection_query_all(MONGODB_CLIENT, DB_NAME, COLLECTION):
    db = MONGODB_CLIENT[DB_NAME]
    col = db[COLLECTION]
    total_documents = col.count_documents({})
    print(f"Total documents to fetch: {total_documents}")

    cursor = col.find()
    documents = list(cursor)  # Directly convert cursor to a list
    jsonified_documents = convert_documents_to_json(documents)

    return jsonified_documents

