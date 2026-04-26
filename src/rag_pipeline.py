import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import pipeline

_script_dir = os.path.dirname(os.path.abspath(__file__))
_default_index_path = os.path.join(_script_dir, "..", "data", "policy_index")

def query_policies(query, index_path=None):
    if index_path is None:
        index_path = _default_index_path
    # Load FAISS index
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={"k": 3})

    # Retrieve docs (new API: invoke)
    results = retriever.invoke(query)

    # Summarize only the top-1 doc for precise answers
    top_doc_text = results[0].page_content if results else "No relevant policies found."
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(top_doc_text, max_length=120, min_length=30, do_sample=False)

    return {
        "query": query,
        "summary": summary[0]['summary_text'],
        "top_k": [doc.page_content for doc in results]
    }

if __name__ == "__main__":
    response = query_policies("What is the parental leave policy?")
    print("Q:", response["query"])
    print("Summary:", response["summary"])
    print("Top-K Policies:", response["top_k"])
