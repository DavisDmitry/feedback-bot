from abc import ABC, abstractmethod
from typing import Optional

from feedback_bot.models import Chat


class AbstractChatRepository(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def get_by_chat_id(self) -> Optional[Chat]:
        pass

    @abstractmethod
    async def get_by_user_id(self) -> Optional[Chat]:
        pass

    @abstractmethod
    async def is_admin_chat(self) -> bool:
        pass

    @abstractmethod
    async def create_chat(self, chat_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    async def remove_by_chat_id(self, chat_id: int) -> None:
        pass
