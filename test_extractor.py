from backend.services.parser import extract_text_and_images
from backend.services.chunker import chunk_paper_text
from backend.services.vector_store import create_vector_db, search_vector_db
from backend.services.generator import reconstruct_section
from backend.services.extractor import extract_insights
from backend.services.exporter import create_reconstructed_document

def run_test():
    pdf_path = "data/sample_paper.pdf"
    
    print("1. Extracting text AND images...")
    # Now unpacking two variables: the text and the list of image paths
    raw_text, image_paths = extract_text_and_images(pdf_path)
    print(f"   -> Extracted {len(image_paths)} graphs/images.")
    
    print("2. Chunking text...")
    chunks = chunk_paper_text(raw_text, chunk_size=400, chunk_overlap=50)
    
    print("3. Connecting to Vector Database...")
    create_vector_db(chunks)
    
    print("\n--- PHASE 4: TEXT RECONSTRUCTION ---")
    abstract_results = search_vector_db("Abstract introduction background problem solution", k=3)
    reconstructed_abstract = reconstruct_section("The Abstract of the paper", abstract_results)
    
    print("\n--- PHASE 5: ADVANCED INSIGHT & MATH EXTRACTION ---")
    # We expand our query to include mathematical terms and conclusion keywords
    extraction_query = "datasets evaluation metrics architecture proposed method equation formula calculation loss function conclusion summary"
    insight_results = search_vector_db(extraction_query, k=6)
    insights = extract_insights(insight_results)
    
    print("\n--- PHASE 6: COMPILING ADVANCED WORD DOCUMENT ---")
    # Pass the images into the document generator
    output_path = create_reconstructed_document(reconstructed_abstract, insights, image_paths, "Advanced_Paper_Report.docx")
    
    print("\n==============================================")
    print("SUCCESS: Advanced AI Report Compiled!")
    print(f"Saved Document to: {output_path}")
    print("==============================================")

if __name__ == "__main__":
    run_test()