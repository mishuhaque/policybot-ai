![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

# 📘 PolicyBot – AI Policy Assistant

An **AI-powered assistant** that makes company policies instantly accessible and understandable.  
Instead of searching through 100+ page PDFs, **PolicyBot retrieves the most relevant snippets and summarizes them into clear answers** with source references.  

---

## 🚀 Features
- ✅ Retrieve top-K relevant policy snippets (RAG + FAISS + LangChain)  
- ✅ Summarize into clear, exec-friendly responses (BART, Flan-T5, XSum)  
- ✅ Always return **answer + source context** for compliance  
- ✅ Deployable API with **FastAPI**  
- ✅ Containerized for production with **Docker**  
- ✅ Optional Slack / MS Teams integration  

---

## 📂 Project Structure
```bash
policybot-ai/
├── src/
│   ├── ingest.py          # Upload & index policies
│   ├── rag_pipeline.py    # Retrieval + summarization
│   ├── app.py             # FastAPI chatbot API
│   └── utils.py           # Shared helpers
├── notebooks/             # Demo notebooks
│   ├── 01_ingest_demo.ipynb
│   └── 02_chat_demo.ipynb
├── data/                  # Sample policies (HR/IT/Compliance)
├── Dockerfile             # Container build
├── requirements.txt       # Dependencies
└── README.md
```

⚡ Quick Start (One-Click Setup)

```
# Clone repository
git clone https://github.com/mishuhaque/policybot-ai.git
cd policybot-ai

# Install dependencies
pip install -r requirements.txt

# Ingest company policies
python src/ingest.py --path data/sample_policies/

# Run FastAPI server
uvicorn src.app:app --reload
# API available at: http://127.0.0.1:8000/docs

# ---- Docker Setup ----
# Build Docker image
docker build -t policybot-ai .

# Run container
docker run -p 8000:8000 policybot-ai
# API available at: http://127.0.0.1:8000/docs

```

📡 Example Request

```
curl -X POST "http://127.0.0.1:8000/query" \
-H "Content-Type: application/json" \
-d '{"question":"What is the parental leave policy?"}'

```

Example Response

```
{
  "answer": "Employees are entitled to 12 weeks parental leave with job protection under FMLA.",
  "source": "HR Policy, Section 5.3"
}

```


📊 ROI Example

Scenario: 5,000 Employees

Avg. salary: $40/hour

6 lookups/year × 30 mins each → 15,000 hours wasted

Lost productivity: $600K/year

✅ With PolicyBot → 80% faster lookups → $480K saved annually
✅ At 50,000 employees → $4.8M saved/year

🧪 Tests


```
pytest tests/


```

📜 License

This project is licensed under the MIT License
.

📬 Contact

👤 Author: Ahshanul Haque
📧 Email: ahshanul.haque@student.nmt.edu
