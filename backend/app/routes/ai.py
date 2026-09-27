from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.ai import AIChatRequest, AIChatResponse
from backend.app.ai.services.chat_service import chat_service
from backend.app.ai.rag.service import index_documents, search

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])


@router.post("/chat", response_model=AIChatResponse)
def ai_chat(request: AIChatRequest, db: Session = Depends(get_db)):
    """Send a message to the FinSight AI Copilot.

    The message is processed through the LangGraph workflow which:
    1. Classifies intent (finance, documentation, general)
    2. Routes to appropriate handler (tools, RAG)
    3. Returns a grounded answer
    """
    return chat_service(
        db,
        request.message,
    )


@router.post("/rag/index")
def rag_index():
    """Re-index all FinSight documentation into the RAG vector store.

    Loads docs from docs/, database/schema/, database/queries/.
    Splits into chunks and indexes with sentence-transformer embeddings.
    """
    result = index_documents()
    return result


@router.get("/rag/search")
def rag_search(q: str, k: int = 4):
    """Search the RAG knowledge base for relevant documentation."""
    return search(q, k=k)
