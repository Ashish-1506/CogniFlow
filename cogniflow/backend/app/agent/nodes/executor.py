import json

from ..state import AgentState
from ..tools.mcp_client import mcp_query_jira, mcp_query_notion


def _select_tool(step: str):
    normalized = step.lower()
    if any(keyword in normalized for keyword in ("jira", "ticket", "blocker", "status", "risk")):
        return mcp_query_jira, {"jql_query": step}
    if any(keyword in normalized for keyword in ("notion", "okr", "goal", "objective")):
        return mcp_query_notion, {"page_title": step}
    return mcp_query_jira, {"jql_query": step}


def executor_node(state: AgentState) -> dict:
    current_step = state["current_step"]
    if current_step >= len(state["plan"]):
        return {}

    tool, arguments = _select_tool(state["plan"][current_step])
    try:
        raw_output = tool.invoke(arguments)
        evidence = json.loads(raw_output) if isinstance(raw_output, str) else raw_output
        evidence["plan_step"] = state["plan"][current_step]
        return {
            "gathered_evidence": [*state["gathered_evidence"], evidence],
            "current_step": current_step + 1,
        }
    except Exception as error:
        retry_count = state.get("retry_count", 0) + 1
        error_message = {
            "role": "tool_error",
            "content": f"Tool execution failed on step {current_step + 1}: {error}",
        }
        return {
            "messages": [*state["messages"], error_message],
            "retry_count": retry_count,
        }
