from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app, get_memory_manager


class FakeMemoryManager:
    def __init__(self):
        self.queries = []
        self.short_term = SimpleNamespace(add_message=lambda *args: None)

    def get_context(self, user_id, session_id, query):
        self.queries.append((user_id, session_id, query))
        return {"long_term_facts": [], "short_term_messages": []}


class FakeAgentGraph:
    async def astream_events(self, state, version):
        assert version == "v2"
        yield {"event": "on_tool_start", "name": "mcp_query_jira", "data": {}}
        yield {"event": "on_chat_model_stream", "name": "synthesizer", "data": {"chunk": "The final"}}


def test_health_endpoint():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "CogniFlow Backend"}


def test_websocket_streams_status_tool_token_complete():
    memory = FakeMemoryManager()
    app.dependency_overrides[get_memory_manager] = lambda: memory
    try:
        with patch("app.main.agent_app", FakeAgentGraph()):
            with TestClient(app).websocket_connect("/ws/chat/session-1") as websocket:
                websocket.send_json({"user_id": "user-1", "query": "Find blockers"})
                payloads = [websocket.receive_json() for _ in range(4)]

        assert [payload["type"] for payload in payloads] == [
            "status",
            "tool",
            "token",
            "complete",
        ]
        assert payloads[0]["data"] == "Planning steps..."
        assert payloads[1]["data"] == "Querying Jira..."
        assert payloads[2]["data"] == "The final"
        assert payloads[3]["data"] == "The final"
        assert memory.queries == [("user-1", "session-1", "Find blockers")]
    finally:
        app.dependency_overrides.pop(get_memory_manager, None)
