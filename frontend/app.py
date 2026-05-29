import streamlit as st
import os
import sys
import tempfile

# Force Python to find the backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.parser import extract_text_and_images
from backend.services.chunker import chunk_paper_text
from backend.services.vector_store import create_vector_db, search_vector_db
from backend.services.generator import reconstruct_section, answer_research_question
from backend.services.extractor import extract_insights
from backend.services.exporter import create_reconstructed_document

# --- 1. SLEEK UI CONFIGURATION ---
st.set_page_config(page_title="AI Research Engine", page_icon="🧬", layout="wide")

# Custom CSS for a highly aesthetic, modern look
st.markdown("""
    <style>
    .main {background-color: #0E1117;}
    h1, h2, h3 {color: #00FFB2 !important; font-weight: 600;}
    .stButton>button {
        background-color: #00FFB2; 
        color: #0E1117; 
        border-radius: 8px; 
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00CC8E; 
        border-color: #00FFB2;
    }
    .css-1d391kg {background-color: #161A22;} /* Sidebar styling */
    </style>
""", unsafe_allow_html=True)

st.title("🧬 Multi-Source AI Research Engine")
st.markdown("*Upload multiple academic papers. Extract insights, compile reports, and chat with your literature.*")

# --- 2. SESSION STATE INIT ---
# We use this to remember if the DB has been built and to store chat history
if "db_ready" not in st.session_state:
    st.session_state.db_ready = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 3. SIDEBAR & MULTI-FILE UPLOAD ---
with st.sidebar:
    st.header("📂 Document Vault")
    # THE MAGIC SWITCH: accept_multiple_files=True
    uploaded_files = st.file_uploader("Upload Research PDFs", type="pdf", accept_multiple_files=True)
    
    if st.button("Process & Build Memory", use_container_width=True):
        if not uploaded_files:
            st.error("Please upload at least one PDF.")
        else:
            with st.status("Building AI Memory Bank...", expanded=True) as status:
                all_raw_text = ""
                all_image_paths = []
                
                # Loop through ALL uploaded files and stitch them together
                for idx, file in enumerate(uploaded_files):
                    st.write(f"Parsing Document {idx+1}/{len(uploaded_files)}: {file.name}...")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(file.getvalue())
                        temp_pdf_path = tmp_file.name
                        
                    raw_text, img_paths = extract_text_and_images(temp_pdf_path)
                    all_raw_text += f"\n\n--- DOCUMENT: {file.name} ---\n\n" + raw_text
                    all_image_paths.extend(img_paths)
                
                st.write("Slicing combined text into semantic chunks...")
                chunks = chunk_paper_text(all_raw_text, chunk_size=400, chunk_overlap=50)
                
                st.write("Embedding vectors into FastEmbed/ChromaDB...")
                create_vector_db(chunks)
                
                # Save paths to session state for the exporter to use later
                st.session_state.all_image_paths = all_image_paths
                st.session_state.db_ready = True
                status.update(label="Memory Bank Built Successfully!", state="complete", expanded=False)

# --- 4. MAIN DASHBOARD TABS ---
# Only show the tools if the DB is ready
if st.session_state.db_ready:
    tab1, tab2 = st.tabs(["📑 Auto-Report Generation", "💬 Chat with Literature"])
    
    # --- TAB 1: REPORT GENERATION ---
    with tab1:
        st.subheader("Generate Multi-Document Synthesis Report")
        if st.button("Synthesize Executive Report"):
            with st.spinner("Extracting overarching insights across all documents..."):
                abstract_results = search_vector_db("Abstract introduction background problem solution overarching theme", k=4)
                reconstructed_abstract = reconstruct_section("A combined executive abstract summarizing all provided documents", abstract_results)
                
                insight_results = search_vector_db("datasets evaluation metrics architecture proposed method equation calculation conclusion summary", k=8)
                insights = extract_insights(insight_results)
                
                output_docx_path = create_reconstructed_document(
                    reconstructed_abstract, 
                    insights, 
                    st.session_state.all_image_paths, 
                    "Multi_Paper_Report.docx"
                )
                
            st.success("Report Compiled!")
            
            # Display Quick Insights
            st.markdown("### 📊 Consolidated Metrics")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Core Contribution:**\n{insights.core_contribution}")
                st.info(f"**Combined Architectures:**\n{insights.architecture}")
            with col2:
                st.success(f"**All Datasets:**\n{', '.join(insights.datasets)}")
                st.json(insights.key_metrics)
                
            with open(output_docx_path, "rb") as file:
                st.download_button(
                    label="📥 Download Consolidated Word Document",
                    data=file,
                    file_name="Multi_Paper_AI_Report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

    # --- TAB 2: INTERACTIVE Q&A CHAT ---
    with tab2:
        st.subheader("Explore Your Documents")
        
        # Render existing chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        # Accept user input
        if prompt := st.chat_input("Ask a question about the uploaded papers..."):
            # Add user message to UI
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Searching literature..."):
                    # Retrieve context specific to the user's question
                    relevant_chunks = search_vector_db(prompt, k=5)
                    # Pass it to Groq
                    response = answer_research_question(prompt, relevant_chunks)
                    st.markdown(response)
                    
            # Save AI response to history
            st.session_state.chat_history.append({"role": "assistant", "content": response})

else:
    # Empty State Instructions
    st.info("👈 Please upload one or more PDFs in the sidebar and click 'Process & Build Memory' to activate the AI Engine.")