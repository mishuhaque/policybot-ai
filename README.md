# 📘 PolicyBot – AI Policy Assistant

🚀 An **AI-powered policy assistant** that makes company policies instantly accessible and understandable.  
Instead of searching through 100+ page PDFs, PolicyBot retrieves the **most relevant policies** and generates **clear, concise summaries** in seconds.  

---

## ✨ Why It Matters
- ⏱️ **Save time** → Employees spend minutes, not hours, finding the right policy.  
- 👩‍💼 **Reduce HR/IT load** → Teams answer fewer repetitive questions.  
- ✅ **Increase compliance clarity** → Always deliver summaries *with source context*.  
- 💰 **Lower costs** → Automates routine policy Q&A, reducing operational overhead.  

PolicyBot empowers organizations to **scale knowledge access** without scaling headcount.  

---

## 🛠️ Tech Stack
- **RAG (Retrieval-Augmented Generation)** → retrieves top-K relevant policy snippets.  
- **Summarization Models (BART, XSum)** → condenses long text into exec-friendly answers.  
- **LangChain + FAISS** → vector search over unlimited documents.  
- **Sentence Transformers** → embeddings (`all-MiniLM-L6-v2`).  
- **FastAPI** → lightweight chatbot API.  
- *(Optional)* **Streamlit / React** → employee-facing chatbot UI.  

---

## 📂 Project Structure
```bash
policybot-ai/
├── README.md              # Project overview
├── requirements.txt       # Dependencies
├── src/
│   ├── ingest.py          # Upload & index unlimited policies
│   ├── rag_pipeline.py    # Retrieval + summarization logic
│   ├── app.py             # FastAPI chatbot API
│   └── utils.py           # Shared helpers
├── notebooks/
│   ├── 01_ingest_demo.ipynb
│   └── 02_chat_demo.ipynb
└── data/
    └── sample_policies/   # Demo HR/IT/Compliance policies
