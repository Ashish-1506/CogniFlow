from functools import lru_cache
import json
from typing import Any

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .agent.graph import app as agent_app
from .config import settings
from .memory.manager import MemoryManager
from .schemas.memory import ContextResponse, FactCreate
from .ws_manager import ConnectionManager

app = FastAPI(title="CogniFlow Backend")
connection_manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache
def get_memory_manager() -> MemoryManager:
    return MemoryManager()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "CogniFlow Backend"}


@app.post("/api/memory/fact", status_code=201)
def save_fact(
    payload: FactCreate,
    memory_manager: MemoryManager = Depends(get_memory_manager),
) -> dict[str, str]:
    memory_manager.long_term.store_fact(
        payload.user_id, payload.fact, payload.metadata
    )
    return {"status": "stored"}


@app.get("/api/memory/context", response_model=ContextResponse)
def get_memory_context(
    user_id: str,
    session_id: str,
    query: str,
    memory_manager: MemoryManager = Depends(get_memory_manager),
) -> ContextResponse:
    return ContextResponse(
        **memory_manager.get_context(user_id, session_id, query)
    )


def _event_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(_event_text(item) for item in value)
    if isinstance(value, dict):
        return _event_text(value.get("text", value.get("content", "")))
    return _event_text(getattr(value, "content", ""))


def _final_response(output: Any) -> str:
    if not isinstance(output, dict):
        return ""
    messages = output.get("messages", [])
    if not messages:
        return ""
    return _event_text(messages[-1])


@app.websocket("/ws/chat/{session_id}")
async def chat_websocket(
    websocket: WebSocket,
    session_id: str,
    memory_manager: MemoryManager = Depends(get_memory_manager),
) -> None:
    await connection_manager.connect(websocket)
    try:
        while True:
            raw_message = await websocket.receive_text()
            try:
                request = json.loads(raw_message)
            except json.JSONDecodeError:
                request = {"query": raw_message}

            if isinstance(request, str):
                request = {"query": request}
            query = str(request.get("query", "")).strip()
            user_id = str(request.get("user_id", session_id)).strip()
            if not query:
                await connection_manager.send_message(
                    {"type": "error", "data": "A query is required."}, websocket
                )
                continue

            context = memory_manager.get_context(user_id, session_id, query)
            initial_state = {
                "messages": [],
                "user_query": query,
                "memory_context": json.dumps(context, default=str),
                "plan": [],
                "current_step": 0,
                "gathered_evidence": [],
                "retry_count": 0,
            }
            final_response = ""
            await connection_manager.send_message(
                {"type": "status", "data": "Planning steps..."}, websocket
            )

            async for event in agent_app.astream_events(initial_state, version="v2"):
                event_name = event.get("event", "")
                event_data = event.get("data", {})
                runnable_name = event.get("name", "")
                if event_name == "on_chat_model_stream":
                    token = _event_text(event_data.get("chunk"))
                    if token:
                        final_response += token
                        await connection_manager.send_message(
                            {"type": "token", "data": token}, websocket
                        )
                elif event_name == "on_tool_start":
                    tool_label = "Querying Jira..." if "jira" in runnable_name.lower() else "Querying Notion..."
                    await connection_manager.send_message(
                        {"type": "tool", "data": tool_label}, websocket
                    )
                elif event_name == "on_tool_end":
                    await connection_manager.send_message(
                        {"type": "status", "data": "Evidence received."}, websocket
                    )
                elif event_name == "on_chain_start" and runnable_name in {"Planner", "Executor", "Synthesizer"}:
                    await connection_manager.send_message(
                        {"type": "status", "data": f"{runnable_name} started..."}, websocket
                    )
                elif event_name == "on_chain_end" and runnable_name == "Synthesizer":
                    final_response = _final_response(event_data.get("output")) or final_response

            if not final_response:
                final_response = "The agent completed without a synthesized response."
            memory_manager.short_term.add_message(session_id, "user", query)
            memory_manager.short_term.add_message(session_id, "assistant", final_response)
            await connection_manager.send_message(
                {"type": "complete", "data": final_response}, websocket
            )
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
