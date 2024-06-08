from pymongo import MongoClient

# Function to query documents by specific fields
def collection_query_by_fields(MONGODB_CLIENT, DB_NAME, COLLECTION, INPUT_DICT):
    db = MONGODB_CLIENT[DB_NAME]
    col = db[COLLECTION]
    # Use the INPUT_DICT directly in the find method
    doc = col.find(INPUT_DICT)
    return doc


