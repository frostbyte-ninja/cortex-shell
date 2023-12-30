from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any


class IHandler(ABC):
    @abstractmethod
    def get_completion(self, **kwargs: Any) -> Generator[str, None, None]:
        raise NotImplementedError

    @abstractmethod
    def handle(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError
