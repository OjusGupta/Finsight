"""Chroma vector store for FinSight RAG.

Provides a persistent Chroma collection that stores embedded
documentation chunks for semantic retrieval.
"""
from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.documents import Document

from backend.app.ai.rag.embeddings import get_embeddings

# Persist directory at project root level
CHROMA_DIR = str(Path(__file__).resolve().parents[4] / ".chroma_db")
COLLECTION_NAME = "finsight_docs"


def get_vector_store() -> Chroma:
    """Return the persistent Chroma vector store instance."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )


def rebuild_vector_store(chunks: list[Document]) -> Chroma:
    """Rebuild the vector store from scratch with the given document chunks.

    Deletes existing collection and re-indexes all chunks.
    Returns the new vector store.
    """
    import shutil

    # Remove old data
    chroma_path = Path(CHROMA_DIR)
    if chroma_path.exists():
        shutil.rmtree(chroma_path)

    # Create new store with all chunks
    store = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR,
    )
    return store
