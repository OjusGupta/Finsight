"""RAG service for FinSight.

Provides high-level operations:
- index_documents(): load, split, and index all FinSight docs
- search(): semantic search against indexed knowledge
"""
from backend.app.ai.rag.loaders import load_all_documents
from backend.app.ai.rag.splitter import split_documents
from backend.app.ai.rag.vector_store import rebuild_vector_store, get_vector_store
from backend.app.ai.rag.retriever import retrieve_context


def index_documents() -> dict:
    """Load all FinSight documentation, split into chunks, and index into Chroma.

    Returns a summary dict with counts.
    """
    documents = load_all_documents()
    chunks = split_documents(documents)
    rebuild_vector_store(chunks)
    return {
        "documents_loaded": len(documents),
        "chunks_indexed": len(chunks),
        "status": "ok",
    }


def search(query: str, k: int = 4) -> dict:
    """Search the RAG knowledge base.

    Returns retrieved context and source metadata.
    """
    store = get_vector_store()
    results = store.similarity_search_with_score(query, k=k)
    items = []
    for doc, score in results:
        items.append({
            "content": doc.page_content[:500],
            "source": doc.metadata.get("source", "unknown"),
            "score": round(float(score), 4),
        })
    return {
        "query": query,
        "results": items,
        "count": len(items),
    }
