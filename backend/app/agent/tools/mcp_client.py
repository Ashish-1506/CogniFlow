import json
from typing import Any

from langchain_core.tools import tool


@tool
def mcp_query_jira(jql_query: str) -> str:
    """Simulate an MCP query for active Jira blockers and Project X statuses."""
    return json.dumps(
        {
            "source": "jira",
            "query": jql_query,
            "project": "Project X",
            "active_blockers": [
                {
                    "ticket": "Jira-402",
                    "summary": "Payment API timeout in production",
                    "status": "Blocked",
                    "owner": "Platform Team",
                },
                {
                    "ticket": "Jira-417",
                    "summary": "Quarterly export misses regional data",
                    "status": "In Progress",
                    "owner": "Data Team",
                },
            ],
        }
    )


@tool
def mcp_query_notion(page_title: str) -> str:
    """Simulate an MCP query for Q3 OKRs and Project X goals in Notion."""
    return json.dumps(
        {
            "source": "notion",
            "page_title": page_title,
            "project": "Project X",
            "q3_okrs": [
                "Reduce payment failures below 0.5%.",
                "Ship the regional reporting export before quarter close.",
            ],
            "project_goals": [
                "Improve reliability for enterprise customers.",
                "Give stakeholders weekly, evidence-based risk updates.",
            ],
        }
    )
