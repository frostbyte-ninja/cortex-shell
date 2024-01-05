from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Generator

    from ..types import Message


class IClient(ABC):  # pragma: no cover
    @abstractmethod
    def get_completion(
        self,
        messages: list[Message],
        model: str,
        temperature: float,
        top_probability: float,
        stream: bool,
        caching: bool,
    ) -> Generator[str, None, None]:
        raise NotImplementedError
