import chromadb
from chromadb.utils import to_dict


class ChromaDBQuery:
    def __init__(self):
        self.client = chromadb.Client()
        self.chat_history_collection = self.client.get_collection('chat_history')
        self.reviews_collection = self.client.get_collection('reviews')

    def query_chat_history(self, session_id):
        query = {'session_id': session_id}
        documents = self.chat_history_collection.find(query)
        return to_dict(documents)

    def query_reviews(self, review_id):
        query = {'review_id': review_id}
        documents = self.reviews_collection.find(query)
        return to_dict(documents)


# Example usage
if __name__ == "__main__":
    query = ChromaDBQuery()
    chat_history = query.query_chat_history('session_123')
    print(f"Queried chat_history: {chat_history}")

    review = query.query_reviews('review_456')
    print(f"Queried review: {review}")
