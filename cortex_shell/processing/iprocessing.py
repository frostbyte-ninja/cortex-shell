from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..types import Message


class IProcessing(ABC):  # pragma: no cover
    @abstractmethod
    def get_messages(self, prompt: str) -> list[Message]:
        raise NotImplementedError

    @abstractmethod
    def postprocessing(self, messages: list[Message]) -> None:
        pass

    @abstractmethod
    def print_history(self) -> None:
        pass
