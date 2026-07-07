# Research Reconstructor

End-to-end MLOps pipeline that digests research paper PDFs, extracts text
and charts, builds a knowledge graph, and synthesizes a polished `.docx`
executive summary.

## Architecture

- **Local text extraction (zero-cost):** Ollama (`llama3.1:8b`) + LangChain's
  `LLMGraphTransformer` extract entities/relationships from paper text.
- **Cloud vision & synthesis:** Groq-hosted models (a vision-capable model
  for charts, a text model for the final report) analyze charts and write
  the report prose — at Groq's characteristically fast inference speed.
- **Cloud graph storage:** Neo4j AuraDB stores the extracted knowledge graph.
- **Frontend:** Streamlit app (`frontend/app.py`) ties it all together and
  compiles the final `.docx` via `python-docx`.

## Setup

1. Install [Ollama](https://ollama.com) locally and pull the model:
   ```bash
   ollama pull llama3.2:3b
   ```
2. Create a Neo4j AuraDB free-tier instance and note its unique database id
   (e.g. `fa59faf1`).
3. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run

```bash
streamlit run frontend/app.py
```

## Project Structure

```
.
├── .env.example
├── requirements.txt
├── backend/
│   └── services/
│       ├── graph_store.py   # Ollama + Neo4j Aura graph pipeline
│       └── vision.py        # PDF chart extraction + GPT-4o vision
└── frontend/
    └── app.py                # Streamlit UI + report synthesis + docx compiler
```

## Known Quirks (do not "fix" these away)

- Neo4j URI must use the `neo4j+ssc://` scheme, and the database name must be
  pinned to the actual Aura database id — not left as default `neo4j`.
- Chart images are always downscaled/re-compressed via PIL before being sent
  to the Groq Vision API, to avoid oversized multimodal payloads.
- The Groq client is built with a custom `httpx.Client(timeout=180.0)` to
  avoid Windows `wsarecv` socket aborts during long generations.
- Groq deprecates/rotates its model lineup frequently. `GROQ_VISION_MODEL`
  and `GROQ_TEXT_MODEL` are both configurable via `.env` — check
  [console.groq.com/docs/models](https://console.groq.com/docs/models) and
  [console.groq.com/docs/vision](https://console.groq.com/docs/vision) if
  you hit a "model decommissioned" error.
- The `.docx` compiler always checks `isinstance(entry, dict)` before reading
  chart analysis results, to avoid crashing on skipped/fallback entries.
