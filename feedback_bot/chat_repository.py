import sqlite3 as sqlite
from abc import ABC, abstractmethod
from typing import Optional

from feedback_bot.models import Chat


class AbstractChatRepository(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def get_by_chat_id(self, chat_id: int) -> Optional[Chat]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Optional[Chat]:
        pass

    @abstractmethod
    async def is_admin_chat(self, chat_id: int) -> bool:
        pass

    @abstractmethod
    async def create_chat(self, chat_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    async def remove_by_chat_id(self, chat_id: int) -> None:
        pass


class SQLiteChatRepository(AbstractChatRepository):
    def __init__(self, conn: sqlite.Connection):
        super().__init__(self)
        self._conn = conn

    def create_table(self) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS chats ("
            "chat_id integer PRIMARY KEY,"
            "user_id integer NOT NULL UNIQUE"
            ");"
        )
        cur.close()

    async def get_by_chat_id(self, chat_id: int) -> Optional[Chat]:
        cur = self._conn.cursor()
        cur.execute(f"SELECT * FROM chats WHERE chat_id = {chat_id}")
        row = cur.fetchone()
        cur.close()
        if not row:
            return None
        return Chat(*row)

    async def get_by_user_id(self, user_id: int) -> Optional[Chat]:
        cur = self._conn.cursor()
        cur.execute(f"SELECT * FROM chats WHERE user_id = {user_id}")
        row = cur.fetchone()
        cur.close()
        if not row:
            return None
        return Chat(*row)

    async def is_admin_chat(self, chat_id: int) -> bool:
        return bool(await self.get_by_chat_id(chat_id))

    async def create_chat(self, chat_id: int, user_id: int) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO chats (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id)
        )
        self._conn.commit()
        cur.close()

    async def remove_by_chat_id(self, chat_id: int) -> None:
        cur = self._conn.cursor()
        cur.execute(f"DELETE FROM images WHERE chat_id = {chat_id}")
        self._conn.commit()
        cur.close()
