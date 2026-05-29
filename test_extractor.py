from backend.services.parser import extract_text_from_pdf
from backend.services.chunker import chunk_paper_text
from backend.services.vector_store import create_vector_db, search_vector_db
from backend.services.generator import reconstruct_section
from backend.services.extractor import extract_insights
from backend.services.exporter import create_reconstructed_document

def run_test():
    pdf_path = "data/sample_paper.pdf"
    
    print("1. Extracting text from source layout...")
    raw_text = extract_text_from_pdf(pdf_path)
    
    print("2. Slicing document into token-aware context chunks...")
    chunks = chunk_paper_text(raw_text, chunk_size=800, chunk_overlap=150)
    
    print("3. Committing chunks to offline vector storage...")
    create_vector_db(chunks)
    
    print("\n--- PHASE 4: TEXT RECONSTRUCTION ---")
    abstract_results = search_vector_db("Abstract introduction background problem solution", k=3)
    reconstructed_abstract = reconstruct_section("The Abstract of the paper", abstract_results)
    print("Abstract successfully synthesized.")
    
    print("\n--- PHASE 5: STRUCTURED INSIGHT EXTRACTION ---")
    extraction_query = "datasets used evaluation metrics results architecture model design proposed method"
    insight_results = search_vector_db(extraction_query, k=5)
    insights = extract_insights(insight_results)
    print("Structured JSON metadata gathered.")
    
    print("\n--- PHASE 6: COMPILING WORD DOCUMENT ---")
    output_path = create_reconstructed_document(reconstructed_abstract, insights, "PEFT_Arena_Reconstructed.docx")
    
    print("\n==============================================")
    print("SUCCESS: Full AI Reconstruction Pipeline Complete!")
    print(f"Saved Document to: {output_path}")
    print("==============================================")

if __name__ == "__main__":
    run_test()