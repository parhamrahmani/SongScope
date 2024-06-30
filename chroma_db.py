"""
chroma_db.py

This file is for creating, inserting, updating, and deleting and querying data from the ChromaDB collections.

"""
import os

import chromadb
from chromadb.utils import embedding_functions

CHROMADB_CLIENT = chromadb.PersistentClient(path="./chromadb")
CHROMADB_EMBEDDING = embedding_functions.DefaultEmbeddingFunction()


def insert_chat_message(thread_id, message, response, timestamp):
    try:
        # Get or create chat_history collection
        chat_history = CHROMADB_CLIENT.get_or_create_collection(
            name='chat_history',
            embedding_function=CHROMADB_EMBEDDING
        )

        # Combine user message and assistant response into a single string
        combined_message = f"User: {message}\nAssistant: {response}"

        # Convert timestamp to string
        timestamp_str = str(timestamp)

        # Add the message to the collection
        chat_history.add(
            documents=[combined_message],  # Pass a list containing a single string
            metadatas=[{"timestamp": timestamp_str, "thread_id": thread_id}],
            ids=[f"{thread_id}_{timestamp_str}"]  # Use a unique ID for each message
        )

        print(f"Message in thread {thread_id} inserted successfully to chat history")
        return f"Message in thread {thread_id} inserted successfully to chat history"
    except Exception as e:
        print(f"Error inserting chat message: {str(e)}")
        # If the collection doesn't exist, try to create it
        if "Collection chat_history is not created" in str(e):
            try:
                CHROMADB_CLIENT.create_collection(
                    name='chat_history',
                    embedding_function=CHROMADB_EMBEDDING
                )
                print("Created chat_history collection")
                # Retry insertion
                return insert_chat_message(thread_id, message, response, timestamp)
            except Exception as create_error:
                print(f"Error creating chat_history collection: {str(create_error)}")
        return f"Failed to insert message in thread {thread_id}: {str(e)}"


def insert_review(review_text, musician_info, timestamp):
    # Get reviews collection
    reviews = CHROMADB_CLIENT.get_or_create_collection(name='chat_history',
                                                       embedding_function=CHROMADB_EMBEDDING)

    # Add the review to the collection
    reviews.add(
        documents=[review_text],
        metadatas=[{"timestamp": timestamp, "musician_info": musician_info}],
        ids=[f"{musician_info}_{timestamp}"]
    )

    return f"Review inserted successfully"


def query(query_text, collection_name, num_results):
    # Get the collection
    collection = CHROMADB_CLIENT.get_or_create_collection(
        name=collection_name,
        embedding_function=CHROMADB_EMBEDDING
    )

    # Perform the query
    results = collection.query(
        query_texts=[query_text],
        n_results=num_results
    )

    return results
