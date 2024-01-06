from __future__ import annotations

from typing import TYPE_CHECKING

from ..history.ihistory import IHistory

if TYPE_CHECKING:  # pragma: no cover
    from ..types import Message


class VolatileHistory(IHistory):
    def __init__(self) -> None:
        self._messages: list[Message] = []

    def messages(self) -> list[Message]:
        return self._messages

    def process_messages(self, messages: list[Message]) -> None:
        self._messages = messages

    def print_history(self) -> None:
        pass
