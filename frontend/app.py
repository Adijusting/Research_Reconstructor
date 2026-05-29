import streamlit as st
import os
import tempfile
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.services.parser import extract_text_and_images
from backend.services.chunker import chunk_paper_text
from backend.services.vector_store import create_vector_db, search_vector_db
from backend.services.generator import reconstruct_section
from backend.services.extractor import extract_insights
from backend.services.exporter import create_reconstructed_document

# --- UI Configuration ---
st.set_page_config(page_title="AI Research Reconstructor", layout="wide")
st.title("📄 AI Research Paper Reconstructor")
st.markdown("Upload a complex academic PDF, and the AI will extract the core methodology, metrics, and math, synthesizing a clean Word document.")

# --- Sidebar ---
with st.sidebar:
    st.header("1. Upload Paper")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    st.markdown("---")
    st.write("**Pipeline Status:**")
    status_text = st.empty()
    status_text.info("Awaiting file upload...")

# --- Main Logic ---
if uploaded_file is not None:
    # 1. Save the uploaded file temporarily so our backend can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_pdf_path = tmp_file.name

    st.success("File uploaded successfully! Click below to start the AI engine.")
    
    if st.button("Run AI Reconstruction Pipeline", type="primary"):
        
        # We use st.spinner to give the user visual feedback during heavy processing
        with st.spinner("Extracting multi-modal layout (Text & Images)..."):
            raw_text, image_paths = extract_text_and_images(temp_pdf_path)
            
        with st.spinner("Chunking and mapping semantic memory..."):
            chunks = chunk_paper_text(raw_text, chunk_size=400, chunk_overlap=50)
            create_vector_db(chunks)
            
        with st.spinner("Synthesizing Reconstructed Abstract..."):
            abstract_results = search_vector_db("Abstract introduction background problem solution", k=3)
            reconstructed_abstract = reconstruct_section("The Abstract of the paper", abstract_results)
            
        with st.spinner("Extracting structured metadata and math..."):
            extraction_query = "datasets evaluation metrics architecture proposed method equation formula calculation loss function conclusion summary"
            insight_results = search_vector_db(extraction_query, k=6)
            insights = extract_insights(insight_results)
            
        with st.spinner("Compiling final Word Document..."):
            output_docx_path = create_reconstructed_document(reconstructed_abstract, insights, image_paths, "Streamlit_Export.docx")
            
        st.balloons()
        status_text.success("Processing Complete!")
        
        # --- Display Results ---
        st.header("📊 Extracted Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Core Contribution")
            st.write(insights.core_contribution)
            st.subheader("Architecture")
            st.write(insights.architecture)
            
        with col2:
            st.subheader("Key Metrics")
            st.json(insights.key_metrics)
            st.subheader("Datasets")
            st.write(", ".join(insights.datasets))
            
        st.markdown("---")
        
        # --- Download Button ---
        with open(output_docx_path, "rb") as file:
            btn = st.download_button(
                label="📥 Download Reconstructed Word Document",
                data=file,
                file_name="AI_Reconstructed_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )