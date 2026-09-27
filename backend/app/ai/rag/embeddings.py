"""Embedding provider for FinSight RAG.

Uses HuggingFace sentence-transformers for local, free, no-API-key embeddings.
Falls back to Google Generative AI embeddings if HuggingFace is unavailable.
"""
from langchain_huggingface import HuggingFaceEmbeddings

# all-MiniLM-L6-v2: fast, small, good quality for retrieval
_MODEL_NAME = "all-MiniLM-L6-v2"


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return the embedding model instance used across the RAG pipeline."""
    return HuggingFaceEmbeddings(
        model_name=_MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
