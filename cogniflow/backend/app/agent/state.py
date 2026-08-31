from typing import Any, TypedDict


class AgentState(TypedDict):
    messages: list[Any]
    user_query: str
    memory_context: str
    plan: list[str]
    current_step: int
    gathered_evidence: list[dict[str, Any]]
    retry_count: int
