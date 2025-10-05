"""Query the FAISS index and summarize the most relevant policy snippet."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from pydantic import BaseModel, Field
from transformers import pipeline

DEFAULT_INDEX_PATH = Path("../data/policy_index")
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_SUMMARIZER_MODEL = "facebook/bart-large-cnn"
SUMMARY_CONFIG = {"max_length": 120, "min_length": 30, "do_sample": False}


class PolicyAnswer(BaseModel):
    """Structured response returned to API clients."""

    query: str = Field(..., description="Original user query")
    summary: str = Field(..., description="Generated summary for the top policy match")
    top_k: List[str] = Field(default_factory=list, description="Raw policy excerpts considered for the answer")


@lru_cache(maxsize=4)
def _get_embeddings(model_name: str) -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=model_name)


@lru_cache(maxsize=2)
def _get_summarizer(model_name: str):
    return pipeline("summarization", model=model_name)


def _load_vector_store(index_path: Path, embeddings: HuggingFaceEmbeddings) -> FAISS:
    if not index_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found at {index_path}. Run src/ingest.py to build it first."
        )

    return FAISS.load_local(str(index_path), embeddings, allow_dangerous_deserialization=True)


def query_policies(
    query: str,
    index_path: Path | str = DEFAULT_INDEX_PATH,
    *,
    top_k: int = 3,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    summarizer_model: str = DEFAULT_SUMMARIZER_MODEL,
) -> PolicyAnswer:
    """Retrieve and summarize policies relevant to *query*.

    Parameters
    ----------
    query:
        End-user question to forward to the vector store.
    index_path:
        Location of the FAISS index directory generated during ingestion.
    top_k:
        Number of documents to fetch from the retriever.
    embedding_model:
        Sentence transformer used during retrieval.
    summarizer_model:
        Hugging Face summarization model used to condense the top document.
    """

    if not query or not query.strip():
        raise ValueError("Query must be a non-empty string.")
    if top_k < 1:
        raise ValueError("top_k must be greater than or equal to 1.")

    embeddings = _get_embeddings(embedding_model)
    vector_store = _load_vector_store(Path(index_path).expanduser().resolve(), embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    documents = retriever.invoke(query)

    top_documents = [doc.page_content for doc in documents]
    if top_documents:
        summarizer = _get_summarizer(summarizer_model)
        summary_result = summarizer(top_documents[0], **SUMMARY_CONFIG)
        summary_text = summary_result[0]["summary_text"].strip()
    else:
        summary_text = "No relevant policies found."

    return PolicyAnswer(query=query, summary=summary_text, top_k=top_documents)


if __name__ == "__main__":
    response = query_policies("What is the parental leave policy?")
    print("Q:", response.query)
    print("Summary:", response.summary)
    print("Top-K Policies:", response.top_k)
