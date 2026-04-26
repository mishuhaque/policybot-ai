# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PolicyBot** is an AI-powered RAG (Retrieval-Augmented Generation) assistant that makes policy documents searchable via an API. Users query the system with natural language questions, and PolicyBot retrieves the most relevant policy snippets and returns a summarized answer with supporting context.

## Architecture & Data Flow

### Core Components

1. **Ingestion Pipeline** (`src/ingest.py`)
   - Takes raw policy documents (list of strings)
   - Chunks them with `RecursiveCharacterTextSplitter` (default: 500 chars, 50 char overlap)
   - Embeds chunks using `sentence-transformers/all-MiniLM-L6-v2` via `HuggingFaceEmbeddings`
   - Stores embeddings in FAISS vector index for fast retrieval
   - Index saved to `data/policy_index/`

2. **RAG Query Pipeline** (`src/rag_pipeline.py`)
   - Loads FAISS index and retrieves top-3 most similar chunks to the query
   - Summarizes the highest-ranked chunk using `facebook/bart-large-cnn` model
   - Returns: query string, summary text, and all retrieved chunks

3. **API Server** (`src/app.py`)
   - FastAPI application with two endpoints:
     - `GET /` → health check
     - `POST /ask` → accepts form field `query`, returns RAG result as JSON
   - Form data requires `python-multipart` library

4. **Utilities** (`src/utils.py`)
   - `clean_text()` - strips whitespace and normalizes spacing

### Path Handling

**Important:** File paths in `rag_pipeline.py` and `ingest.py` are calculated relative to the script location (not working directory), allowing the API to be called from any directory. The default index path is `../data/policy_index` relative to `src/`.

## Common Commands

**Install dependencies:**
```bash
pip install -r requirements.txt
pip install python-multipart  # Required for form data handling
```

**Build/rebuild FAISS index from policy documents:**
```bash
python src/ingest.py
```
Edit the `sample_policies` list in `ingest.py` or call `build_index()` programmatically with your own policy texts.

**Run API server:**
```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```
Defaults to `http://127.0.0.1:8000`. Use `--reload` for development (auto-restarts on file changes).

**Query the API (cURL):**
```bash
# Health check
curl http://127.0.0.1:8000/

# Ask a question
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=What is the parental leave policy?"
```

**Test RAG pipeline directly:**
```bash
python -c "from src.rag_pipeline import query_policies; print(query_policies('Your question'))"
```

## Configuration & Tuning

- **Chunk size/overlap** – Edit `chunk_size` and `chunk_overlap` in `ingest.py`'s `RecursiveCharacterTextSplitter` to match document structure
- **Retrieval depth** – Adjust `search_kwargs={"k": 3}` in `rag_pipeline.py` to retrieve more/fewer snippets
- **Summarizer model** – Swap `facebook/bart-large-cnn` in `rag_pipeline.py` with a smaller model (e.g., `sshleifer/distilbart-cnn-12-6`) if GPU memory is limited
- **Embedding model** – Currently `sentence-transformers/all-MiniLM-L6-v2` (light, fast). Switch to `all-mpnet-base-v2` for higher quality at the cost of size/speed

## Important Notes

- **LangChain deprecation warnings** are expected for `HuggingFaceEmbeddings` and `FAISS.load_local()` – the code uses `allow_dangerous_deserialization=True` per LangChain ≥0.1.0 requirements
- **First-run download** – The BART summarizer (~1.5GB) downloads on first use; subsequent runs use the cached model
- **GPU availability** – Models will use GPU if available (Apple Silicon uses `mps:0`); force CPU with `device=-1` in pipeline if needed
- **Index location** – Both `ingest.py` and `rag_pipeline.py` default to `data/policy_index`. For production with shared storage, override the `index_path` parameter when calling functions

## Testing & Validation

No formal test suite exists yet. Validate with:
- Notebooks in `notebooks/` – interactive demos for chunking and querying
- Direct API calls via cURL or Python requests
- Custom test scripts calling `query_policies()` with known questions

## Dependencies

See `requirements.txt`. Key packages:
- `torch`, `transformers`, `sentence-transformers` – ML models
- `faiss-cpu` – vector search
- `langchain` – text splitting and retrieval orchestration
- `fastapi`, `uvicorn` – API server
- `python-multipart` – form data parsing (added manually if missing)
