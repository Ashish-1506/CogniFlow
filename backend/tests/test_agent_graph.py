from typing import Any

from app.agent.graph import create_graph


class StructuredModel:
    def __init__(self, schema: Any):
        self.schema = schema

    def invoke(self, prompt: str):
        if self.schema.__name__ == "PlanOutput":
            return self.schema(steps=[{"step": "Query Jira for active blockers"}, {"step": "Read Notion Q3 OKRs"}])
        return self.schema(response="Project X has one active blocker [Jira-402]; its Q3 goals are reliability and reporting [Notion-Q3].")


class FakeLLM:
    def with_structured_output(self, schema: Any) -> StructuredModel:
        return StructuredModel(schema)


def test_graph_executes_plan_and_loops_until_synthesis() -> None:
    graph = create_graph(FakeLLM(), interrupt_before=[])
    result = graph.invoke(
        {
            "messages": [],
            "user_query": "Summarize Project X risks and Q3 goals",
            "memory_context": "The user is a project manager.",
            "plan": [],
            "current_step": 0,
            "gathered_evidence": [],
            "retry_count": 0,
        }
        ,
        config={"configurable": {"thread_id": "agent-test"}},
    )

    assert result["current_step"] == 2
    assert len(result["gathered_evidence"]) == 2
    assert result["gathered_evidence"][0]["source"] == "jira"
    assert result["gathered_evidence"][1]["source"] == "notion"
    assert result["messages"][-1]["content"].startswith("Project X")
