"""State definition for the FinSight LangGraph workflow.

Uses TypedDict for clean state management across graph nodes.
"""
from typing import TypedDict, Any


class AgentState(TypedDict, total=False):
    """State object that flows through the FinSight AI graph.

    Fields:
        user_message: The original user query.
        intent: Classified intent (finance_query, rag_query, general).
        rag_context: Retrieved documentation context from RAG.
        tool_results: Results from finance tool calls.
        final_answer: The generated response to return to the user.
        tool_calls: List of tool calls made during processing.
        error: Error message if something went wrong.
    """
    user_message: str
    intent: str
    rag_context: str
    tool_results: list[dict[str, Any]]
    final_answer: str
    tool_calls: list[dict[str, Any]]
    error: str | None
    messages: list[Any]
    tool_calls_pending: list[dict[str, Any]]
