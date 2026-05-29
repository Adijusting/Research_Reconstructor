import os
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# 1. Define the strict data schema
# This tells LLM exactly what fields we want ad what data type they must be
class PaperInsights(BaseModel):
    architecture: str = Field(
        description= "The main ML architecture, neural network, or algorithm proposed in the paper."
        
    )
    datasets: list[str] = Field(
        description= "A list of the specific datasets used for training and evaluation."
    )
    key_metrics: dict[str, str] =Field(
        description="Key performance metrics reported. Format as {'Metric Name': 'Value}, Example: {'Accuracy':'95.4%'}"
    )
    core_contribution: str=Field(
        description="A strict, 1-sentence summary of the paper's primary scientific contribution."
    )
    
def extract_insights(retrieved_context: list)->PaperInsights:
    """
    Forces LLM to read the context and output a strict JSON.
    """
    
    # Initialize the LLM (Temperature 0 is crucial here so it does not hallucinate)
    llm = ChatGroq(
        temperature=0.0,
        model_name = "llama-3.3-70b-versatile",
        api_key = os.getenv("GROQ_API_KEY")
    )
    
    structured_llm = llm.with_structured_output(PaperInsights)
    
    context_text = "\n\n----\n\n".join([doc.page_content for doc in retrieved_context])
    
    system_prompt = """
    You are an expert AI data extraction tool.
    Extract the requested inormation from the provided academic text.
    If a specific detail (like an dataset or metric) is not mentioned in the text, output "Not Specified" or leave the list/dictionary empty.
    Do NOT invent information.
    
    CONTEXT:
    {context}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt), ("human", "Extract the stuctured insights.")
    ])
    
    chain = prompt | structured_llm
    
    result = chain.invoke({"context": context_text})
    
    return result
    
    
    
    