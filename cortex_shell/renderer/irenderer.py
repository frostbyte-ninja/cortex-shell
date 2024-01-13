from __future__ import annotations

from abc import ABC, abstractmethod


class IRenderer(ABC):  # pragma: no cover
    @abstractmethod
    def __enter__(self) -> IRenderer:
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, *args: object) -> None:
        raise NotImplementedError

    @abstractmethod
    def __call__(self, text: str, chunk: str) -> None:
        raise NotImplementedError
