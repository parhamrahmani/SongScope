
def query_mongodb(MONGODB_CLIENT, DB_NAME, COLLECTIONS):
    db = MONGODB_CLIENT[DB_NAME]
    results = {}

    # Query the collections
    for collection in COLLECTIONS:
        print(f"Querying collection: {collection}")
        results[collection] = list(db[collection].find())

    return results
