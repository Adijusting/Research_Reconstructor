from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_chroma import Chroma
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "chroma_db")

def get_embedding_model():
    """
    Uses FastEmbed with the absolute lightest model available,
    locked to a single thread to prevent any memory spikes.
    """
    from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
    
    return FastEmbedEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2", # The ultra-light model
        batch_size=8,  # Tiny batch size
        threads=1      # Strictly single-threaded execution
    )

def create_vector_db(chunks: list[str], collection_name: str = "research_paper"):
    """
    Embeds the text chunks locally and stores them in ChromaDB.
    """
    try:
        embeddings = get_embedding_model()
        
        vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory=DB_DIR
        )
        
        return vector_store
    except Exception as e:
        print(f"Error creating vector database: {str(e)}")
        return None

def search_vector_db(query: str, collection_name: str = "research_paper", k: int = 2):
    """
    Searches the database for the most semantically relevant chunks.
    """
    embeddings = get_embedding_model()
    vector_store = Chroma(
        collection_name=collection_name, 
        embedding_function=embeddings, 
        persist_directory=DB_DIR
    )
    
    results = vector_store.similarity_search(query, k=k)
    return results