import chromadb

class ChromaDBSetup:
    def __init__(self):
        self.client = chromadb.Client()

    def create_collections(self):
        try:
            self.client.create_collection('chat_history')
            print("Collection 'chat_history' created.")
        except ValueError:
            print("Collection 'chat_history' already exists.")

        try:
            self.client.create_collection('reviews')
            print("Collection 'reviews' created.")
        except ValueError:
            print("Collection 'reviews' already exists.")

# Example usage
if __name__ == "__main__":
    setup = ChromaDBSetup()
    setup.create_collections()
