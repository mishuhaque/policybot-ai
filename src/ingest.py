import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

def build_index(policy_texts, save_path="../data/policy_index"):
    # Split policies into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents(policy_texts)

    # Use MiniLM embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Build FAISS index
    db = FAISS.from_documents(docs, embeddings)

    # Save locally
    os.makedirs(save_path, exist_ok=True)
    db.save_local(save_path)

    print(f"✅ Index saved at {save_path}")

if __name__ == "__main__":
    sample_policies = [
        "HR Policy: Employees are entitled to 12 weeks parental leave.",
        "IT Policy: Passwords must be updated every 90 days.",
        "Compliance Policy: All customer data must follow GDPR regulations."
    ]
    build_index(sample_policies)
