import chromadb


class ChromaDBInsertion:
    def __init__(self):
        self.client = chromadb.Client()
        self.chat_history_collection = self.ensure_collection('chat_history')
        self.reviews_collection = self.ensure_collection('reviews')

    def ensure_collection(self, collection_name):
        try:
            return self.client.get_collection(collection_name)
        except ValueError:
            self.client.create_collection(collection_name)
            return self.client.get_collection(collection_name)

    def insert_chat_history(self, session_id, messages):
        document_ids = [f"{session_id}_{i}" for i, _ in enumerate(messages)]
        documents = [{'session_id': session_id, 'message': msg} for msg in messages]
        self.chat_history_collection.add(
            ids=document_ids,
            embeddings=None,  # Assuming embeddings are not required
            metadatas=documents,
            documents=None  # Or set to a list of actual document contents if applicable
        )
        print(f"Inserted chat history for session {session_id} with messages: {messages}")

    def insert_review(self, review_id, review_text):
        self.reviews_collection.add(
            ids=[review_id],
            embeddings=None,  # Assuming embeddings are not required
            metadatas=[{'review_id': review_id, 'review_text': review_text}],
            documents=None  # Or set to a list of actual document contents if applicable
        )
        print(f"Inserted review {review_id} with text: {review_text}")

# Example usage
if __name__ == "__main__":
    inserter = ChromaDBInsertion()
    inserter.insert_chat_history('session_123', [('user', 'Hello'), ('bot', 'Hi, how can I help you?')])
    inserter.insert_review('review_456', 'This is a sample review.')
