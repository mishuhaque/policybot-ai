# 📘 PolicyBot – AI Policy Assistant

🚀 **PolicyBot** is an **AI-powered assistant** that makes company policies instantly accessible and understandable.  
Instead of searching through 100+ page PDFs, PolicyBot retrieves the **most relevant policies** and generates **clear, concise summaries** in seconds.  

---

## ✨ Why It Matters
- ⏱️ **Save employee time** – No more scrolling through massive policy handbooks.  
- 👩‍💼 **Reduce HR/IT workload** – Automates repetitive Q&A around leave, IT rules, compliance.  
- ✅ **Clarity + Compliance** – Always delivers summaries *with source context* to avoid misinterpretation.  
- 💰 **Cost savings** – Reduces manual support, freeing staff for higher-value tasks.  

📊 **Example Impact:**  
- A 5,000-employee company saves ~2,500 staff hours per year by automating policy lookup.  
- HR support tickets drop by **40%** when employees self-serve policy answers.  

PolicyBot empowers organizations to **scale knowledge access** without scaling headcount.  

---

## 🆚 Why PolicyBot is Superior
### ❌ Traditional Approach
- Static intranet pages or PDFs.  
- Search is keyword-only → often irrelevant.  
- Employees waste time or contact HR for clarification.  

### ❌ Human Support
- Inconsistent answers depending on who responds.  
- Costly → requires HR, IT, compliance staff time.  
- Not scalable across large organizations.  

### ✅ PolicyBot (RAG + LangChain)
- **Retrieves** top-K relevant policy snippets via vector search.  
- **Summarizes** in exec-friendly language using AI.  
- **Explains with context** → answer + original source snippet.  
- **Scales infinitely** → handles unlimited policies and questions.  

---

## 💡 Example Use Cases

🔹 **HR Policy Example**  
**Q:** *What is the parental leave policy?*  
**A:** Employees are entitled to **12 weeks parental leave**, with job protection under FMLA.  
*(Source: HR Policy, Section 5.3)*  

🔹 **IT Security Example**  
**Q:** *When do I need to update my password?*  
**A:** All employees must update passwords **every 90 days**.  
*(Source: IT Security Policy, Section 2.1)*  

🔹 **Compliance Example**  
**Q:** *How do we handle customer data under GDPR?*  
**A:** Customer data must be stored in **encrypted databases** and deleted upon request within 30 days.  
*(Source: Compliance Policy, GDPR Clause 4.2)*  

---

## 🛠️ Tech Stack
- **RAG (Retrieval-Augmented Generation)** → fetches top-K relevant policies.  
- **Summarization Models (BART, Flan-T5, XSum)** → condense long text into exec-friendly summaries.  
- **LangChain + FAISS** → scalable vector search.  
- **Sentence Transformers** → embeddings (`all-MiniLM-L6-v2`).  
- **FastAPI** → chatbot API for integration into Slack/MS Teams.  
- *(Optional)* **Streamlit / React** → build employee-facing chatbot UI.  

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



# 1. Install dependencies
pip install -r requirements.txt

# 2. Ingest your company policies
python src/ingest.py --path data/sample_policies/

# 3. Run retrieval + summarization pipeline
python src/rag_pipeline.py

# 4. Start chatbot API
uvicorn src.app:app --reload


## 📊 Business ROI Calculator
  
Here’s a simple ROI model for **PolicyBot**:

### Scenario: 5,000 Employees
- Average salary: **$40/hour**  
- Policy lookups per employee: **6 per year**  
- Time wasted per lookup: **30 minutes**

---

### ❌ Without PolicyBot
- 5,000 × 6 × 0.5 hrs = **15,000 hours wasted/year**  
- 15,000 × $40 = **$600,000 lost productivity/year**

---

### ✅ With PolicyBot (80% faster)
- Only **3,000 hours wasted/year**  
- **$480,000 saved annually**

---

💡 **Scales with company size**:  
A 50,000-employee enterprise can save **$4.8M per year**.

 

