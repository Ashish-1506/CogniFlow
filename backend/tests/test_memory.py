from pathlib import Path

import pytest

from app.memory.long_term import LongTermMemory
from app.memory.manager import MemoryManager
from app.memory.short_term import ShortTermMemory


class DeterministicEmbeddingFunction:
    def name(self) -> str:
        return "deterministic-test"

    def _embed(self, input: list[str]) -> list[list[float]]:
        vectors = []
        for text in input:
            normalized = text.lower()
            vectors.append(
                [
                    float("jira" in normalized),
                    float("manager" in normalized),
                    float("python" in normalized),
                ]
            )
        return vectors

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self._embed(input)

    def embed_documents(self, input: list[str]) -> list[list[float]]:
        return self._embed(input)

    def embed_query(self, input: list[str]) -> list[list[float]]:
        return self._embed(input)


def test_short_term_history_persists_and_respects_limit(tmp_path: Path) -> None:
    db_path = tmp_path / "conversations.db"
    first_instance = ShortTermMemory(str(db_path))
    first_instance.add_message("session-1", "user", "Find my open tickets")
    first_instance.add_message("session-1", "assistant", "I found two tickets")
    first_instance.add_message("other-session", "user", "Ignore this")

    second_instance = ShortTermMemory(str(db_path))
    history = second_instance.get_session_history("session-1", limit=1)

    assert history[0]["role"] == "assistant"
    assert history[0]["content"] == "I found two tickets"
    second_instance.clear_session("session-1")
    assert second_instance.get_session_history("session-1") == []


def test_long_term_facts_persist_and_filter_by_user(tmp_path: Path) -> None:
    persist_dir = tmp_path / "chroma"
    embedding_function = DeterministicEmbeddingFunction()
    first_instance = LongTermMemory(
        str(persist_dir), embedding_function=embedding_function
    )
    first_instance.store_fact("user-1", "The team tracks work in Jira")
    first_instance.store_fact("user-2", "The team uses Python")

    second_instance = LongTermMemory(
        str(persist_dir), embedding_function=embedding_function
    )
    facts = second_instance.query_relevant_facts("user-1", "Jira tickets")

    assert facts == ["The team tracks work in Jira"]


def test_manager_combines_both_memory_layers(tmp_path: Path) -> None:
    short_term = ShortTermMemory(str(tmp_path / "conversations.db"))
    long_term = LongTermMemory(
        str(tmp_path / "chroma"),
        embedding_function=DeterministicEmbeddingFunction(),
    )
    short_term.add_message("session-1", "user", "What is our Jira risk?")
    long_term.store_fact("user-1", "The team tracks work in Jira")

    context = MemoryManager(short_term, long_term).get_context(
        "user-1", "session-1", "Jira risk"
    )

    assert context["long_term_facts"] == ["The team tracks work in Jira"]
    assert context["short_term_messages"][0]["content"] == "What is our Jira risk?"
