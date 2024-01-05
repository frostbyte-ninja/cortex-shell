from __future__ import annotations

from typing import TYPE_CHECKING

from rich import print as rich_print
from rich.rule import Rule

from ..chat_session import ChatSession
from ..history.ihistory import IHistory

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from ..types import Message


class PersistentHistory(IHistory):
    def __init__(self, chat_id: str, history_size: int, history_path: Path) -> None:
        super().__init__()
        self._chat_id = chat_id
        self._chat_session = ChatSession(self._chat_id, history_size, history_path)

    def get_messages(self) -> list[Message]:
        return self._chat_session.get_messages()

    def process_messages(self, messages: list[Message]) -> None:
        self._chat_session.write_messages(messages)

    def print_history(self) -> None:
        if self._chat_session.exists():
            rich_print(Rule(title="Chat History", style="bold magenta"))
            self._chat_session.show_messages(self._chat_session)
            rich_print(Rule(style="bold magenta"))
