import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

def get_llm():
    """
    Initializes teh Groq LLM, we are using Llama-3 70B. Temperature is set to 0.1 
    to keep output factual and prevent halucinations.
    """
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the .env file")
    
    return ChatGroq(
        temperature=0.1,
        model_name = "llama-3.3-70b-versatile",
        api_key=api_key
    )
    
def reconstruct_section(query: str, retrieved_context: list) -> str:
    """
    Takes the retireved academic chunks and forces the LLM to reconstruct a section
    """
    
    llm = get_llm()
    
    context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_context])
    
    system_prompt = """
    You are an expert AI academic researcher and technical writer.
    Your goal is to reconstruct sections of research paper based strictly on the provided context.
    
    RULES:
    1. Base your answer ONLY on the provided context.
    2. Do NOT hallucinate or invent metrics, datasets or architectures.
    3. If the provided context does not contain enough information to fully answer the prompt, state what is missing.
    4. Write in a professional, academic tone suitable for a research paper.
    
    CONTEXT TO USE:
    {context}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Please write/reconstruct the folloeing sections: {query}")
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({
        "context": context_text,
        "query": query
    })
    
    return response.content
    