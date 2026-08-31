from typing import Any

from ..config import settings
from .long_term import LongTermMemory
from .short_term import ShortTermMemory


class MemoryManager:
    """Coordinates short-term session context and long-term user facts."""

    def __init__(
        self,
        short_term: ShortTermMemory | None = None,
        long_term: LongTermMemory | None = None,
        short_term_limit: int = 10,
    ):
        self.short_term = short_term or ShortTermMemory(settings.sqlite_db_path)
        self.long_term = long_term or LongTermMemory(
            settings.chroma_persist_dir, settings.default_embedding_model
        )
        self.short_term_limit = short_term_limit

    def get_context(self, user_id: str, session_id: str, query: str) -> dict[str, Any]:
        return {
            "long_term_facts": self.long_term.query_relevant_facts(user_id, query),
            "short_term_messages": self.short_term.get_session_history(
                session_id, self.short_term_limit
            ),
        }
