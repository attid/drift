import sqlite3
from pathlib import Path


class ConversationStore:
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def get(self, telegram_chat_id: int) -> int | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT drift_conversation_id FROM conversations WHERE telegram_chat_id = ?",
                (telegram_chat_id,),
            ).fetchone()
        return int(row[0]) if row else None

    def set(self, telegram_chat_id: int, drift_conversation_id: int) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO conversations (telegram_chat_id, drift_conversation_id)
                VALUES (?, ?)
                ON CONFLICT(telegram_chat_id)
                DO UPDATE SET drift_conversation_id = excluded.drift_conversation_id
                """,
                (telegram_chat_id, drift_conversation_id),
            )

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    telegram_chat_id INTEGER PRIMARY KEY,
                    drift_conversation_id INTEGER NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._path)
