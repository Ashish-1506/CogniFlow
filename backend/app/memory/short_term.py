import sqlite3
from pathlib import Path


class ShortTermMemory:
    """SQLite-backed conversation history for active sessions."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_session_id "
                "ON messages (session_id, id)"
            )

    def add_message(self, session_id: str, role: str, content: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content),
            )

    def get_session_history(self, session_id: str, limit: int = 10) -> list[dict]:
        if limit < 1:
            return []

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()

        return [dict(row) for row in reversed(rows)]

    def clear_session(self, session_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM messages WHERE session_id = ?", (session_id,)
            )
