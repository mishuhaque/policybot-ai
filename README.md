# 📘 PolicyBot – AI Policy Assistant  
![Visitors](https://visitor-badge.glitch.me/badge?page_id=mishuhaque.policybot-ai)

**License:** MIT  
**Language:** Python  
**Framework:** FastAPI  
**Deployment:** Docker  

---

## 📖 Overview
**PolicyBot** is an **AI-powered assistant** that makes company policies instantly accessible and understandable.  
Instead of scrolling through 100+ page PDFs, employees get **clear, concise answers with source references** in seconds.  

---

## 🚀 Key Features
- ⏱️ **Save time** – eliminates policy lookup frustration.  
- 👩‍💼 **Reduce HR/IT workload** – automates repetitive Q&A.  
- ✅ **Clarity & Compliance** – always provides source context.  
- 💰 **Cost Savings** – reduces manual support overhead.  

**Example Impact:**  
- 5,000 employees → **2,500 staff hours saved/year**.  
- HR support tickets ↓ **40%** with self-service answers.  

---

## 🆚 Why PolicyBot?
| Traditional Approach | Human Support | PolicyBot ✅ |
|----------------------|---------------|--------------|
| Static PDFs / intranet | Inconsistent answers | RAG-powered retrieval |
| Keyword-only search | Costly (HR/IT time) | Summarized, exec-friendly |
| Time wasted | Not scalable | Unlimited scalability |

---

## 💡 Example Queries
- **HR:** *What is the parental leave policy?*  
  → Employees are entitled to **12 weeks parental leave** *(HR Policy §5.3)*  

- **IT Security:** *When do I need to update my password?*  
  → Passwords must be updated **every 90 days** *(IT Security Policy §2.1)*  

- **Compliance:** *How do we handle GDPR requests?*  
  → Customer data stored in **encrypted DBs**; deletion within 30 days *(GDPR Policy §4.2)*  

---

## 🛠️ Tech Stack
- **Python + FastAPI** – API layer  
- **LangChain + FAISS** – retrieval & vector search  
- **Sentence Transformers** – embeddings (`all-MiniLM-L6-v2`)  
- **Summarization Models** – BART, Flan-T5, XSum  
- **Docker** – containerized deployment  
- **Optional UI** – Streamlit / React for chat interface  

---

## 📂 Project Structure
```bash
policybot-ai/
├── README.md              # Project overview
├── requirements.txt       # Dependencies
├── Dockerfile             # Containerization
├── src/
│   ├── ingest.py          # Upload & index policies
│   ├── rag_pipeline.py    # Retrieval + summarization logic
│   ├── app.py             # FastAPI chatbot API
│   └── utils.py           # Shared helpers
├── notebooks/
│   ├── 01_ingest_demo.ipynb
│   └── 02_chat_demo.ipynb
└── data/
    └── sample_policies/   # Demo HR/IT/Compliance policies
