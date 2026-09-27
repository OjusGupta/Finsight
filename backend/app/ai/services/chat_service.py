"""FinSight AI Chat Service — LangGraph orchestration.

This is the main entry point for AI chat requests.
Routes through the LangGraph workflow for intent classification,
tool execution, RAG retrieval, and action proposals.

Replaces the previous direct LLM + tool calling approach with
a stateful graph-based workflow.
"""
from sqlalchemy.orm import Session
from backend.app.schemas.ai import AIChatResponse
from backend.app.ai.graph.workflow import finsight_graph

def chat_service(db: Session, message: str) -> AIChatResponse:
    """Process an AI chat message through the LangGraph workflow."""
    try:
        initial_state = {
            "user_message": message,
            "intent": "",
            "rag_context": "",
            "tool_results": [],
            "final_answer": "",
            "tool_calls": [],
            "error": None,
            "messages": [],
            "tool_calls_pending": [],
        }

        result = finsight_graph.invoke(initial_state)

        if result.get("error"):
            return AIChatResponse(
                answer=f"AI Error: {result['error']}",
                intent=result.get("intent"),
            )

        return AIChatResponse(
            answer=result.get("final_answer", "I couldn't generate a response."),
            intent=result.get("intent"),
            tool_calls=result.get("tool_calls") or None,
        )

    except Exception as e:
        return AIChatResponse(
            answer=f"AI Provider Error: {str(e)}",
        )
