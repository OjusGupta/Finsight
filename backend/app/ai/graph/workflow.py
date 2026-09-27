"""LangGraph workflow builder for FinSight AI.
Re-architected to be a true ReAct Supervisor.
"""
from langgraph.graph import StateGraph, END
from backend.app.ai.graph.state import AgentState
from backend.app.ai.graph import nodes

def _should_continue(state: AgentState) -> str:
    """Determine if the agent should continue looping or end."""
    tool_calls = state.get("tool_calls_pending")
    if tool_calls:
        return "execute_tools"
    return END

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("agent", nodes.agent_node)
    graph.add_node("execute_tools", nodes.execute_tools_node)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        _should_continue,
        {
            "execute_tools": "execute_tools",
            END: END
        }
    )
    
    graph.add_edge("execute_tools", "agent")

    return graph.compile()

finsight_graph = build_graph()
