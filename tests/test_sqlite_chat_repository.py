import sqlite3 as sqlite
from typing import Iterator

import pytest

from feedback_bot.chat_repository import SQLiteChatRepository as ChatRepository
from feedback_bot.models import Chat

CHAT_ID = 123123
USER_ID = 321321


pytestmark = pytest.mark.asyncio


@pytest.fixture
def db_conn() -> Iterator[sqlite.Connection]:
    conn = sqlite.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def chat_repo(db_conn: sqlite.Connection) -> ChatRepository:
    repo = ChatRepository(db_conn)
    repo.create_table()
    return repo


@pytest.fixture
def chat_repo_with_row(chat_repo: ChatRepository) -> ChatRepository:
    conn = chat_repo._conn
    conn.execute(
        "INSERT INTO chats (chat_id, user_id) VALUES (?, ?)", (CHAT_ID, USER_ID)
    )
    conn.commit()
    return chat_repo


class TestGetByChatID:
    async def test_with_none(self, chat_repo: ChatRepository):
        assert await chat_repo.get_by_chat_id(CHAT_ID) is None

    async def test_with_row(self, chat_repo_with_row: ChatRepository):
        assert await chat_repo_with_row.get_by_chat_id(CHAT_ID) == Chat(
            CHAT_ID, USER_ID
        )


class TestGetByUserID:
    async def test_with_none(self, chat_repo: ChatRepository):
        assert await chat_repo.get_by_user_id(USER_ID) is None

    async def test_with_row(self, chat_repo_with_row: ChatRepository):
        assert await chat_repo_with_row.get_by_user_id(USER_ID) == Chat(
            CHAT_ID, USER_ID
        )


class TestIsAdminChat:
    async def test_false(self, chat_repo_with_row: ChatRepository):
        assert await chat_repo_with_row.is_admin_chat(123456) is False

    async def test_true(self, chat_repo_with_row: ChatRepository):
        assert await chat_repo_with_row.is_admin_chat(CHAT_ID) is True


async def test_create(chat_repo: ChatRepository):
    await chat_repo.create(CHAT_ID, USER_ID)
    cur = chat_repo._conn.cursor()
    cur.execute("SELECT * FROM chats")
    assert cur.fetchone() == (CHAT_ID, USER_ID)


async def test_remove_chat(chat_repo_with_row: ChatRepository):
    await chat_repo_with_row.remove_by_chat_id(CHAT_ID)
    cur = chat_repo_with_row._conn.cursor()
    cur.execute("SELECT * FROM chats")
    assert cur.fetchall() == []
