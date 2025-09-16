from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import pipeline

def query_policies(query, index_path="../data/policy_index"):
    # Load FAISS index
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={"k": 3})

    # Retrieve docs
    results = retriever.get_relevant_documents(query)
    docs_text = " ".join([doc.page_content for doc in results])

    # Summarize (use BART for now)
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(docs_text, max_length=120, min_length=30, do_sample=False)

    return {
        "query": query,
        "top_k": [doc.page_content for doc in results],
        "summary": summary[0]['summary_text']
    }

if __name__ == "__main__":
    response = query_policies("What is the parental leave policy?")
    print("Q:", response["query"])
    print("Summary:", response["summary"])
    print("Top-K Policies:", response["top_k"])
