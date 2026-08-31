import sqlite3
from pathlib import Path
from typing import Literal

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from ..config import settings
from .nodes.executor import executor_node
from .nodes.planner import create_planner_node, planner_node
from .nodes.synthesizer import create_synthesizer_node, synthesizer_node
from .state import AgentState

MAX_RETRIES = 3


def _route_after_executor(
    state: AgentState,
) -> Literal["planner", "executor", "synthesizer"]:
    last_message = state.get("messages", [])[-1:]
    if last_message and last_message[0].get("role") == "tool_error":
        if state.get("retry_count", 0) < MAX_RETRIES:
            return "planner"
        return "synthesizer"
    if state["current_step"] < len(state["plan"]):
        return "executor"
    return "synthesizer"


def _create_sqlite_checkpointer() -> SqliteSaver:
    database_path = Path(settings.sqlite_db_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(database_path), check_same_thread=False)
    checkpointer = SqliteSaver(connection)
    checkpointer.setup()
    return checkpointer


def create_graph(llm=None, checkpointer=None, interrupt_before=None):
    """Build the plan-and-execute graph with HITL and bounded recovery."""
    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_node if llm is None else create_planner_node(llm))
    graph.add_node("executor", executor_node)
    graph.add_node(
        "synthesizer",
        synthesizer_node if llm is None else create_synthesizer_node(llm),
    )
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "executor")
    graph.add_conditional_edges(
        "executor",
        _route_after_executor,
        {
            "planner": "planner",
            "executor": "executor",
            "synthesizer": "synthesizer",
        },
    )
    graph.add_edge("synthesizer", END)
    saver = checkpointer or _create_sqlite_checkpointer()
    return graph.compile(
        checkpointer=saver,
        interrupt_before=["executor"] if interrupt_before is None else interrupt_before,
    )


app = create_graph()
