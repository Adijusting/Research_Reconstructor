from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_chroma import Chroma
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "chroma_db")

# --- ADD THIS GLOBAL VARIABLE AT THE TOP OF THE FILE ---
_global_embedding_model = None

def get_embedding_model():
    """
    Uses FastEmbed with the absolute lightest model available,
    locked to a single thread. Uses a Singleton pattern to prevent 
    Streamlit from reloading the model into RAM on every chat message.
    """
    global _global_embedding_model
    
    # If the model is already loaded in RAM, just return it!
    if _global_embedding_model is not None:
        return _global_embedding_model
        
    from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
    
    # Otherwise, load it for the very first time
    _global_embedding_model = FastEmbedEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2", 
        batch_size=8,  
        threads=1      
    )
    
    return _global_embedding_model

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