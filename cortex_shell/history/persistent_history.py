from __future__ import annotations

from typing import TYPE_CHECKING

from rich import print as rich_print
from rich.rule import Rule

from ..history.ihistory import IHistory

if TYPE_CHECKING:  # pragma: no cover
    from ..session.chat_session import ChatSession
    from ..session.chat_session_manager import ChatSessionManager
    from ..types import Message


class PersistentHistory(IHistory):
    def __init__(self, chat_id: str, session_manager: ChatSessionManager) -> None:
        super().__init__()
        self._chat_id = chat_id
        self._session_manager = session_manager

    def messages(self) -> list[Message]:
        return self._get_session().messages()

    def process_messages(self, messages: list[Message]) -> None:
        self._get_session().write_messages(messages)

    def print_history(self) -> None:
        if self._get_session().exists():
            rich_print(Rule(title="Chat History", style="bold magenta"))
            self._session_manager.print_messages(self._get_session())
            rich_print(Rule(style="bold magenta"))

    def _get_session(self) -> ChatSession:
        return self._session_manager.get_session(self._chat_id)
