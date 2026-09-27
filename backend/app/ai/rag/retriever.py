"""Retriever for FinSight RAG.

Wraps the Chroma vector store with a similarity search retriever.
"""
from langchain_core.vectorstores import VectorStoreRetriever

from backend.app.ai.rag.vector_store import get_vector_store

# Number of chunks to retrieve per query
DEFAULT_K = 4


def get_retriever(k: int = DEFAULT_K) -> VectorStoreRetriever:
    """Return a retriever that performs similarity search against FinSight docs."""
    store = get_vector_store()
    return store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )


def retrieve_context(query: str, k: int = DEFAULT_K) -> str:
    """Retrieve relevant documentation context for a query.

    Returns a formatted string of the top-k document chunks.
    """
    retriever = get_retriever(k=k)
    docs = retriever.invoke(query)
    if not docs:
        return ""

    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[Source {i}: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)
