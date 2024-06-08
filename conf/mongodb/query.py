from pymongo import MongoClient

# Function to query all documents in a collection
def collection_query_all(MONGODB_CLIENT, DB_NAME, COLLECTION):
    db = MONGODB_CLIENT[DB_NAME]
    results = list(db[COLLECTION].find())
    return results

# Function to query documents by specific fields
def collection_query_by_fields(MONGODB_CLIENT, DB_NAME, COLLECTION, INPUT_DICT):
    db = MONGODB_CLIENT[DB_NAME]
    col = db[COLLECTION]
    # Use the INPUT_DICT directly in the find method
    doc = col.find(INPUT_DICT)
    return doc


# Function to query multiple collections
def query_mongodb(MONGODB_CLIENT, DB_NAME, COLLECTIONS):
    db = MONGODB_CLIENT[DB_NAME]
    results = {}

    # Query the collections
    for collection in COLLECTIONS:
        print(f"Querying collection: {collection}")
        results[collection] = list(db[collection].find())

    return results

