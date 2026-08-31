import sqlite3
from pathlib import Path
from unittest.mock import patch

from langgraph.checkpoint.sqlite import SqliteSaver

from app.agent.graph import create_graph
from app.agent.nodes.planner import PlanOutput
from app.agent.nodes.synthesizer import SynthesisOutput


class StructuredLLM:
    def __init__(self, schema):
        self.schema = schema

    def invoke(self, prompt):
        if self.schema is PlanOutput:
            return PlanOutput(steps=[{"step": "Find Q3 goals in Notion"}])
        return SynthesisOutput(response="Q3 goals prioritize reliability [Notion-Q3].")


class MockLLM:
    def with_structured_output(self, schema):
        return StructuredLLM(schema)


class DestructiveLLM(MockLLM):
    def with_structured_output(self, schema):
        if schema is PlanOutput:
            return type(
                "DestructivePlan",
                (),
                {"invoke": lambda self, prompt: PlanOutput(steps=[{"step": "Delete Jira project data"}])},
            )()
        return super().with_structured_output(schema)


def make_checkpointer(tmp_path: Path) -> SqliteSaver:
    saver = SqliteSaver(
        sqlite3.connect(str(tmp_path / "graph.db"), check_same_thread=False)
    )
    saver.setup()
    return saver


def test_find_goals_transitions_to_synthesis_without_live_services(tmp_path):
    with (
        patch("app.agent.llm.get_llm", return_value=MockLLM()),
        patch(
            "langchain_core.tools.StructuredTool.invoke",
            return_value='{"source": "notion", "q3_okrs": ["Improve reliability"]}',
        ) as notion_query,
    ):
        graph = create_graph(
            checkpointer=make_checkpointer(tmp_path), interrupt_before=[]
        )
        result = graph.invoke(
            {
                "messages": [],
                "user_query": "Find our Q3 goals",
                "memory_context": "",
                "plan": [],
                "current_step": 0,
                "gathered_evidence": [],
                "retry_count": 0,
            },
            config={"configurable": {"thread_id": "goals-test"}},
        )

    assert notion_query.call_count == 1
    assert result["current_step"] == 1
    assert result["gathered_evidence"][0]["source"] == "notion"
    assert result["messages"][-1]["content"] == "Q3 goals prioritize reliability [Notion-Q3]."


def test_tool_failure_replans_only_until_retry_cap(tmp_path):
    with (
        patch("app.agent.llm.get_llm", return_value=MockLLM()),
        patch(
            "langchain_core.tools.StructuredTool.invoke",
            side_effect=RuntimeError("connector unavailable"),
        ),
    ):
        graph = create_graph(
            checkpointer=make_checkpointer(tmp_path), interrupt_before=[]
        )
        result = graph.invoke(
            {
                "messages": [],
                "user_query": "Find our Q3 goals",
                "memory_context": "",
                "plan": [],
                "current_step": 0,
                "gathered_evidence": [],
                "retry_count": 0,
            },
            config={"configurable": {"thread_id": "retry-test"}},
        )

    assert result["retry_count"] == 3
    assert result["messages"][-1]["role"] == "assistant"


def test_tool_failure_routes_back_to_planner(tmp_path):
    llm = MockLLM()
    with patch("app.agent.llm.get_llm", return_value=llm), patch(
        "langchain_core.tools.StructuredTool.invoke",
        side_effect=RuntimeError("connector unavailable"),
    ) as tool_invoke:
        graph = create_graph(checkpointer=make_checkpointer(tmp_path), interrupt_before=[])
        result = graph.invoke(
            {
                "messages": [],
                "user_query": "Find our Q3 goals",
                "memory_context": "",
                "plan": [],
                "current_step": 0,
                "gathered_evidence": [],
                "retry_count": 0,
            },
            config={"configurable": {"thread_id": "planner-retry-test"}},
        )

    assert tool_invoke.call_count == 3
    assert result["retry_count"] == 3
    assert any(message["role"] == "tool_error" for message in result["messages"])


def test_destructive_tool_pauses_at_hitl_breakpoint(tmp_path):
    graph = create_graph(
        DestructiveLLM(), checkpointer=make_checkpointer(tmp_path)
    )
    result = graph.invoke(
        {
            "messages": [],
            "user_query": "Delete project data",
            "memory_context": "",
            "plan": [],
            "current_step": 0,
            "gathered_evidence": [],
            "retry_count": 0,
        },
        config={"configurable": {"thread_id": "hitl-test"}},
    )

    assert result["current_step"] == 0
    assert result["gathered_evidence"] == []
