from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..types import Message


class IHistory(ABC):  # pragma: no cover
    @abstractmethod
    def messages(self) -> list[Message]:
        raise NotImplementedError

    @abstractmethod
    def process_messages(self, messages: list[Message]) -> None:
        raise NotImplementedError

    @abstractmethod
    def print_history(self) -> None:
        raise NotImplementedError
