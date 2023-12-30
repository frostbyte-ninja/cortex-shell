from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import Message


class IPostProcessing(ABC):
    @abstractmethod
    def __call__(self, messages: list[Message]) -> None:
        raise NotImplementedError
