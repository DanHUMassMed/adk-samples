from typing import List
import chromadb
from chromadb.utils import embedding_functions

# --- 1. Initialize the ChromaDB Client and Collection ---
# This setup is run once when your agent starts up.

# Define paths (must match the path used in the loading script)
DB_PATH = "./chroma_db_chunks" 
COLLECTION_NAME = "alphabet_10k_collection_chunks"

# Initialize the embedding function used for both loading and querying
# It must match the model used when the data was indexed.
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Initialize the persistent client and get the specific collection object
try:
    client = chromadb.PersistentClient(path=DB_PATH)
    # The 'collection' variable is now available globally in this module's scope
    collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_function)
    print(f"ChromaDB collection '{COLLECTION_NAME}' loaded successfully.")
except ValueError as e:
    print(f"Error loading collection: {e}. Make sure you ran the PDF loader script first.")
    # Exit or handle error if the collection isn't found

# --- 2. Define the ADK Tool Function ---
# This function is the "tool" the Google ADK agent will call.
# It now correctly accesses the 'collection' variable defined above.

def ask_chromadb(query_text: str) -> List[str]:
    """
    Retrieves relevant document chunks from the ChromaDB knowledge corpus
    based on a user query. This tool should be used when the user asks
    specific questions about the Alphabet Form 10-K document knowledge base.

    Args:
        query_text: The question or query to search for in the knowledge base.

    Returns:
        A list of strings, where each string is a relevant document chunk's content
        including source metadata.
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=3, # Retrieve top 3 relevant results
        include=["documents", "metadatas"]
    )
    
    # Format results for the LLM to read easily (including citation info)
    formatted_results = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        formatted_results.append(
            f"Source: {meta['source']} (Chunk ID: {meta['chunk_id']})\nContent: {doc}\n---"
        )

    # Return a list of strings for the LLM to use as context
    return formatted_results

