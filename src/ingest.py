"""Utilities for converting policy documents into a FAISS vector index."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Sequence

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

from utils import clean_corpus

DEFAULT_INDEX_PATH = Path("../data/policy_index")
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SUPPORTED_SUFFIXES = (".md", ".txt")


def build_index(
    policy_texts: Sequence[str],
    save_path: Path | str = DEFAULT_INDEX_PATH,
    *,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> Path:
    """Create a FAISS index for the provided policy snippets.

    Parameters
    ----------
    policy_texts:
        A sequence of policy strings to ingest.
    save_path:
        Directory where the FAISS index should be persisted.
    chunk_size, chunk_overlap:
        Chunking strategy supplied to :class:`RecursiveCharacterTextSplitter`.
    embedding_model:
        Hugging Face sentence transformer used to generate embeddings.

    Returns
    -------
    pathlib.Path
        The directory containing the saved FAISS index.
    """

    cleaned_policies = clean_corpus(policy_texts)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    documents = splitter.create_documents(cleaned_policies)

    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    vector_store = FAISS.from_documents(documents, embeddings)

    target_path = Path(save_path).expanduser().resolve()
    target_path.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(target_path))

    return target_path


def load_policy_texts(path: Path) -> List[str]:
    """Load plain-text policy files from *path*.

    The loader accepts individual files or directories containing ``.txt`` or
    ``.md`` documents. Files are read using UTF-8 encoding.
    """

    if not path.exists():
        raise FileNotFoundError(f"No policy files found at {path}.")

    if path.is_file():
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise ValueError(
                f"Unsupported file type: {path.suffix}. Expected one of {SUPPORTED_SUFFIXES}."
            )
        return [path.read_text(encoding="utf-8")]

    policy_texts: List[str] = []
    for file_path in sorted(path.rglob("*")):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_SUFFIXES:
            policy_texts.append(file_path.read_text(encoding="utf-8"))

    if not policy_texts:
        raise ValueError(
            f"No supported documents were discovered in {path}. Accepted suffixes: {SUPPORTED_SUFFIXES}."
        )

    return policy_texts


def parse_args(arguments: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the ingestion CLI."""

    parser = argparse.ArgumentParser(description="Build a FAISS index for policy documents.")
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to a policy file or directory containing .txt/.md documents.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_INDEX_PATH,
        help=f"Directory where the FAISS index will be stored (default: {DEFAULT_INDEX_PATH}).",
    )
    parser.add_argument("--chunk-size", type=int, default=500, help="Chunk size for the text splitter (default: 500).")
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="Token overlap between chunks produced by the text splitter (default: 50).",
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default=DEFAULT_EMBEDDING_MODEL,
        help="Sentence transformer model used for embeddings.",
    )

    return parser.parse_args(arguments)


def main() -> Path:
    """Entry point for command-line usage."""

    args = parse_args()

    if args.input:
        policies = load_policy_texts(args.input)
    else:
        policies = SAMPLE_POLICIES

    index_path = build_index(
        policies,
        save_path=args.output,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        embedding_model=args.embedding_model,
    )

    print(f"✅ Index saved at {index_path}")
    return index_path


SAMPLE_POLICIES = (
    "HR Policy: Employees are entitled to 12 weeks parental leave.",
    "IT Policy: Passwords must be updated every 90 days.",
    "Compliance Policy: All customer data must follow GDPR regulations.",
)


if __name__ == "__main__":
    main()
