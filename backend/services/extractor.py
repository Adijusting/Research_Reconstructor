import os
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# 1. Define the strict data schema
# This tells LLM exactly what fields we want ad what data type they must be
class PaperInsights(BaseModel):
    architecture: str = Field(description="The main ML architecture or algorithm.")
    datasets: list[str] = Field(description="Datasets used for training or evaluation.")
    key_metrics: dict[str, str] = Field(description="Key performance metrics. Example: {'Accuracy': '95.4%'}")
    core_contribution: str = Field(description="A 1-sentence summary of the primary contribution.")
    
    # --- NEW FIELD FOR MATH ---
    key_calculations: list[str] = Field(
        description="A list of the 2 to 3 most important mathematical formulas, loss functions, or calculations mentioned in the text."
    )
    
    # --- NEW FIELD FOR SUMMARY ---
    final_summary: str = Field(
        description="Write a comprehensive 1-2 paragraph summary synthesizing the problem, method, and results. Do NOT output 'Not Specified' for this field."
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
    
    RULES:
    1. For factual fields (architecture, datasets, metrics, calculations), extract the exact information. If not found, output "Not Specified" or leave empty.
    2. For the 'final_summary' field, you MUST write and generate a new summary based on the provided context. Do NOT output 'Not Specified' for the summary.
    3. Do NOT hallucinate data outside the context.
    
    CONTEXT:
    {context}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt), ("human", "Extract the stuctured insights.")
    ])
    
    chain = prompt | structured_llm
    
    result = chain.invoke({"context": context_text})
    
    return result
    
    
    
    