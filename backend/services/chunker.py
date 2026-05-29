from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_paper_text(raw_text: str, chunk_size: int = 800, chunk_overlap: int=150)-> list[str]:
    """
    chunk_size = maximum number of tokens per chunk
    chunk_overlap = how many tokens between chunks to preserve content"""
    
    try:
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name="text-embedding-3-small",
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap,
        )
        
        chunks = text_splitter.split_text(raw_text)
        return chunks
    
    except Exception as e:
        print(f"Error during chunking: {str(e)}")
        return []
    
    