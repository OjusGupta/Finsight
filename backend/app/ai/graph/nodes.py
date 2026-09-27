"""Graph nodes for the FinSight LangGraph workflow."""
import json
from backend.app.ai.graph.state import AgentState
from backend.app.ai.llm.provider import get_llm
from backend.app.ai.prompts.finance_prompt import FINANCE_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

def _extract_text(content) -> str:
    if isinstance(content, list):
        return "".join(c.get("text", "") if isinstance(c, dict) else str(c) for c in content)
    return str(content)

def agent_node(state: AgentState) -> AgentState:
    """The central LLM reasoning node."""
    from backend.app.ai.tools.finance_tools import get_finance_tools
    from backend.app.ai.rag.retriever import retrieve_context
    from backend.app.database.session import SessionLocal
    from langchain_core.tools import tool

    db = SessionLocal()
    try:
        llm = get_llm()

        @tool
        def search_knowledge_base(query: str) -> str:
            """Search the FinSight policies and rules knowledge base."""
            return retrieve_context(query, k=3)

        tools = get_finance_tools(db) + [search_knowledge_base]
        llm_with_tools = llm.bind_tools(tools)

        # Build message history: system + all prior messages + new user message
        # Prior messages (tool results, assistant turns) come BEFORE the new user message
        # so the LLM has full context for multi-turn conversations.
        messages = [SystemMessage(content=FINANCE_SYSTEM_PROMPT)]

        # Replay prior conversation turns (maintains entity IDs across turns)
        for msg in state.get("messages", []):
            messages.append(msg)

        # Append the current user message
        messages.append(HumanMessage(content=state["user_message"]))

        ai_msg = llm_with_tools.invoke(messages)

        # Update state messages — store assistant response
        new_messages = list(state.get("messages", [])) + [HumanMessage(content=state["user_message"]), ai_msg]

        # Check if we have tool calls
        if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:

            return {
                **state,
                "messages": new_messages,
                "tool_calls_pending": ai_msg.tool_calls,
                "intent": "analysis"
            }
        else:
            return {
                **state,
                "messages": new_messages,
                "tool_calls_pending": [],
                "final_answer": _extract_text(ai_msg.content),
                "intent": state.get("intent", "general")
            }

    finally:
        db.close()


def execute_tools_node(state: AgentState) -> AgentState:
    """Execute the tools requested by the LLM."""
    from backend.app.ai.tools.finance_tools import get_finance_tools
    from backend.app.ai.rag.retriever import retrieve_context
    from backend.app.database.session import SessionLocal
    from langchain_core.tools import tool

    db = SessionLocal()
    try:
        @tool
        def search_knowledge_base(query: str) -> str:
            """Search the FinSight policies and rules knowledge base."""
            return retrieve_context(query, k=3)
            
        tools = get_finance_tools(db) + [search_knowledge_base]
        tool_map = {tool.name: tool for tool in tools}
        
        new_messages = list(state.get("messages", []))
        tool_results_list = list(state.get("tool_results", []))
        tool_calls_made = list(state.get("tool_calls", []))
        
        for tc in state.get("tool_calls_pending", []):
            tool_calls_made.append({"name": tc["name"], "args": tc.get("args", {})})
            selected = tool_map.get(tc["name"])
            if selected:
                try:
                    tool_msg = selected.invoke(tc)
                    new_messages.append(tool_msg)
                    tool_results_list.append({"tool": tc["name"], "result": str(tool_msg.content)[:2000]})
                except Exception as e:
                    new_messages.append(ToolMessage(content=f"Error: {e}", tool_call_id=tc["id"]))
            else:
                new_messages.append(ToolMessage(content="Tool not found.", tool_call_id=tc["id"]))
                
        return {
            **state,
            "messages": new_messages,
            "tool_calls_pending": [],
            "tool_calls": tool_calls_made,
            "tool_results": tool_results_list
        }
    finally:
        db.close()
