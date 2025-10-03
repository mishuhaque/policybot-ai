![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

# 📘 PolicyBot – AI Policy Assistant

PolicyBot is an **AI-powered retrieval-augmented generation (RAG) assistant** that makes long policy manuals instantly searchable. It ingests policy documents, indexes them with FAISS, retrieves the most relevant snippets, and summarizes them into clear answers—complete with supporting context so compliance teams can trust every response.

---

## 🧭 Table of Contents
1. [Features](#-features)
2. [Architecture](#-architecture)
3. [Getting Started](#-getting-started)
   - [Prerequisites](#prerequisites)
   - [Clone and Install](#clone-and-install)
   - [Set Up Your Index](#set-up-your-index)
   - [Run the API](#run-the-api)
   - [Query the Assistant](#query-the-assistant)
4. [Configuration](#-configuration)
5. [Development Workflow](#-development-workflow)
6. [Docker Usage](#-docker-usage)
7. [Notebooks & Demos](#-notebooks--demos)
8. [Testing](#-testing)
9. [Troubleshooting](#-troubleshooting)
10. [License & Contact](#-license--contact)

---

## 🚀 Features
- ✅ Retrieve top-*k* policy snippets with **FAISS** + **LangChain**
- ✅ Summarize answers via **Hugging Face** summarization models (defaults to `facebook/bart-large-cnn`)
- ✅ Return both the answer and supporting context for auditability
- ✅ Serve the assistant through a lightweight **FastAPI** service
- ✅ Ship the entire pipeline as a **Docker** container for reproducible deployments
- ✅ Provide example policies, notebooks, and scripts to accelerate experimentation

---

## 🧱 Architecture
```
policybot-ai/
├── src/
│   ├── ingest.py          # Build the FAISS index from raw policy text
│   ├── rag_pipeline.py    # Retrieve relevant chunks & summarize the answer
│   ├── app.py             # FastAPI app exposing `GET /` and `POST /ask`
│   └── utils.py           # Shared preprocessing helpers (extend as needed)
├── data/                  # Sample policies & generated FAISS index
├── notebooks/             # Interactive demos for ingestion & querying
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```
1. **Ingestion** – `ingest.py` splits policies into overlapping chunks using `RecursiveCharacterTextSplitter`, embeds them with `sentence-transformers/all-MiniLM-L6-v2`, and stores them in a local FAISS index.
2. **Retrieval + Generation** – `rag_pipeline.py` loads the FAISS index, retrieves the top results for a question, and summarizes the best match with a Hugging Face summarization pipeline.
3. **Serving Layer** – `app.py` wraps the pipeline in a FastAPI service. The `/ask` endpoint accepts a form field called `query` and returns the answer payload.

---

## 🛠 Getting Started

### Prerequisites
- Python **3.9+** (3.10 recommended)
- `pip` for dependency management
- Optional: Docker 20.10+ for containerized runs
- Optional: A Hugging Face token if you plan to use gated models

### Clone and Install
```bash
git clone https://github.com/mishuhaque/policybot-ai.git
cd policybot-ai

# (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### Set Up Your Index
By default, the repository ships with toy policies in `data/`. To build an index with your own documents:
1. Load or parse your policies into a Python list of strings (each string represents one document or section).
2. Update the `sample_policies` list in `src/ingest.py`, or import `build_index` from another script/notebook and pass in your list.
3. Run the script to generate the FAISS artifacts:
   ```bash
   python src/ingest.py
   ```

The index is saved to `data/policy_index` by default. You can change the destination by passing a different `save_path` when calling `build_index` programmatically.

### Run the API
```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```
Available endpoints:
- `GET /` – health check (`{"msg": "PolicyBot API is running"}`)
- `POST /ask` – form submission with `query="Your question"`

### Query the Assistant
Using `curl` with a form body (matches the FastAPI signature):
```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=What is the parental leave policy?"
```
Example JSON response:
```json
{
  "query": "What is the parental leave policy?",
  "summary": "Employees are entitled to 12 weeks parental leave with job protection under FMLA.",
  "top_k": [
    "HR Policy: Employees are entitled to 12 weeks parental leave.",
    "... additional retrieved chunks ..."
  ]
}
```

---

## ⚙️ Configuration
- **Index location** – Both `ingest.py` and `rag_pipeline.py` default to `../data/policy_index`. Change the `save_path` and `index_path` parameters to point to a shared storage location in production.
- **Chunking strategy** – Tune `chunk_size` and `chunk_overlap` in `ingest.py` to match the structure of your policies.
- **Retriever depth** – Adjust `search_kwargs={"k": 3}` to balance recall and latency.
- **Summarizer** – Swap `facebook/bart-large-cnn` with a smaller/faster model (e.g., `sshleifer/distilbart-cnn-12-6`) if GPU resources are limited.
- **Dangerous deserialization** – `FAISS.load_local(..., allow_dangerous_deserialization=True)` is required for LangChain ≥0.1.0. Be mindful when loading untrusted indexes.

---

## 🧑‍💻 Development Workflow
1. Update or extend `src/utils.py` with reusable cleaning utilities.
2. Run `ingest.py` to refresh the FAISS index after adding new documents.
3. Iterate on retrieval settings in `rag_pipeline.py` to improve answer quality.
4. Add API routes or switch to JSON payloads in `src/app.py` as your deployment grows.
5. Capture experiments in the notebooks to share workflows with non-engineers.

---

## 📦 Docker Usage
Build and run the container for a fully reproducible environment:
```bash
docker build -t policybot-ai .
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  policybot-ai
```
Mounting the `data/` volume ensures the container can read the FAISS index you generated on the host.

---

## 📓 Notebooks & Demos
- `notebooks/01_ingest_demo.ipynb` – Walkthrough of chunking, embedding, and storing policies.
- `notebooks/02_chat_demo.ipynb` – Interactive QA demo that mirrors the FastAPI behavior.
Use these as playgrounds for rapid prototyping before updating the production scripts.

---

## ✅ Testing
Unit tests live under `tests/` (add them as the project evolves). Run the suite with:
```bash
pytest tests/
```
If you do not have tests yet, create regression notebooks or scripts to validate retrieval accuracy and summarization quality.

---

## 🛠 Troubleshooting
| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| Hugging Face model download is slow | First-time download of BART (~1.5GB) | Pre-download the model or switch to a smaller summarizer |
| `/ask` returns empty results | FAISS index not found or empty | Re-run `ingest.py` and ensure `index_path` points to the correct directory |
| GPU unavailable error | Summarizer defaults to GPU when available | Force CPU inference with `pipeline(..., device=-1)` |
| Unicode/encoding errors during ingest | Mixed encodings in source documents | Normalize text via `src/utils.py` before indexing |

---

## 📜 License & Contact
This project is licensed under the **MIT License**.

Maintainer: **Ahshanul Haque**  
📧 `ahshanul.haque@student.nmt.edu`
