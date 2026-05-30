# 🧬 Multi-Source AI Research Engine (v2.0)

<p align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-ff4b4b)
![Groq](https://img.shields.io/badge/LLM-Groq_LPU-black)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success)

</p>

---

## 🚀 Overview

**Multi-Source AI Research Engine** is an advanced **Retrieval-Augmented Generation (RAG)** pipeline built for reconstructing, synthesizing, and interacting with academic research papers.

The engine intelligently ingests multiple complex PDFs, builds a unified vector memory, and provides:

* 📚 Cross-paper literature synthesis
* 💬 Interactive research Q&A
* 🧠 Structured insight extraction
* 📄 Automated report generation

Designed specifically for **low-resource hardware**, the system combines:

* ⚡ **FastEmbed** for ultra-lightweight local embeddings
* 🚀 **Groq LPUs** for lightning-fast LLM inference
* 🧩 **ChromaDB** for persistent semantic memory

---

# ✨ What's New in Version 2.0

### 📄 Multi-Document Ingestion

Upload and process multiple academic PDFs simultaneously.
The engine merges them into a unified **“Super-Memory”** vector database for cross-referencing and comparative analysis.

---

### 💬 Interactive Research Chat

A ChatGPT-style conversational interface grounded strictly in uploaded documents.

Ask questions like:

* *“Compare the architectures proposed in Paper A and Paper B.”*
* *“What datasets were used across all papers?”*
* *“Summarize the mathematical formulation sections.”*

with **minimal hallucination** and source-grounded responses.

---

### 🎨 Modern Streamlit Dashboard

A fully redesigned frontend featuring:

* 🌙 Custom dark-mode UI
* ⚡ Real-time processing indicators
* 📑 Interactive tabs
* 📂 Multi-file upload workflow

---

### 🛡️ Memory-Safe Singleton Embedding Engine

FastEmbed is wrapped in a **Singleton architecture** to prevent repeated model initialization and eliminate:

* `bad allocation`
* memory overflow crashes
* redundant embedding loads

during rapid interactions.

---

# 🔥 Core Features

## 📑 Intelligent PDF Parsing

* Handles **multi-column academic layouts**
* Extracts:

  * raw text
  * tables
  * graphs
  * embedded figures/images

using **PyMuPDF**.

---

## 🧠 Llama-3 Research Synthesis

Powered by:

* **Groq API**
* `llama-3.3-70b-versatile`

for:

* methodology reconstruction
* conclusion synthesis
* literature summarization
* contextual Q&A

---

## 📊 Structured Insight Extraction

Uses **Pydantic validation pipelines** to force structured JSON outputs such as:

* Key Metrics
* Datasets
* Equations
* Model Architectures
* Hyperparameters
* Evaluation Results

---

## 📄 Automated DOCX Compilation

Automatically generates highly formatted Microsoft Word reports containing:

* Synthesized explanations
* Extracted metadata
* Embedded images
* Research insights
* Comparative analysis

---

# 🏗️ Project Architecture

```text
research_reconstructor/
│
├── backend/
│   └── services/
│       ├── chunker.py
│       │   └── Token-aware semantic slicing
│       │
│       ├── exporter.py
│       │   └── DOCX compilation engine
│       │
│       ├── extractor.py
│       │   └── Pydantic insight extraction
│       │
│       ├── generator.py
│       │   └── Groq Llama-3 synthesis & chat logic
│       │
│       ├── parser.py
│       │   └── PyMuPDF text & image extraction
│       │
│       └── vector_store.py
│           └── FastEmbed Singleton + ChromaDB
│
├── frontend/
│   └── app.py
│       └── Streamlit dashboard
│
├── data/
│   └── Local storage for:
│       ├── vector DB
│       ├── images
│       └── exported reports
│
├── .env
├── .gitignore
├── requirements.txt
└── test_extractor.py
```

---

# 🛠️ Installation & Setup

## 1️⃣ Prerequisites

Make sure you have:

* Python **3.9+**
* A free **Groq API Key**

---

## 2️⃣ Clone the Repository

```bash
git clone https://github.com/YourUsername/research-reconstructor.git

cd research-reconstructor
```

---

## 3️⃣ Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Mac/Linux

```bash
python -m venv venv

source venv/bin/activate
```

---

## 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY="your_groq_api_key_here"
```

---

# ▶️ Running the Application

Launch the Streamlit dashboard:

```bash
streamlit run frontend/app.py
```

> ⚠️ First Run Notice
> FastEmbed will automatically download the lightweight
> `all-MiniLM-L6-v2` embedding model during the first launch.

---

# 💻 Usage Workflow

## 📤 Step 1 — Upload PDFs

Drag and drop one or more academic papers using the sidebar uploader.

---

## ⚙️ Step 2 — Build Research Memory

Click:

```text
Process & Build Memory
```

to:

* parse documents
* chunk content
* generate embeddings
* populate ChromaDB

---

## 📄 Step 3 — Generate Executive Report

Navigate to:

```text
Auto-Report
```

and click:

```text
Synthesize Executive Report
```

to generate a downloadable `.docx` report.

---

## 💬 Step 4 — Chat with Literature

Switch to:

```text
Chat with Literature
```

and ask questions directly across all uploaded papers.

---

# ⚡ Technology Stack

| Layer               | Technology  |
| ------------------- | ----------- |
| Frontend            | Streamlit   |
| AI Orchestration    | LangChain   |
| Vector Database     | ChromaDB    |
| Local Embeddings    | FastEmbed   |
| LLM Inference       | Groq        |
| PDF Processing      | PyMuPDF     |
| Document Generation | python-docx |

---

# 🧠 Example Use Cases

✅ Literature Review Automation
✅ Research Paper Reconstruction
✅ Academic Q&A Assistant
✅ Methodology Comparison
✅ Automated Research Reports
✅ AI-Powered Research Companion

---

# 📸 Future Improvements

* [ ] Citation-aware responses
* [ ] PDF highlighting & source tracing
* [ ] Multi-user workspace support
* [ ] Research graph visualization
* [ ] Local LLM fallback mode
* [ ] Fine-tuned academic summarization

---

# 📜 License

This project is licensed under the **MIT License**.

Feel free to use, modify, and distribute it for research and educational purposes.

---

# 👨‍💻 Author

Built with ❤️ for researchers, students, and AI enthusiasts.

If you like this project, consider ⭐ starring the repository.
