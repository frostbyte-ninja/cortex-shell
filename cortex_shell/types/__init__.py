from __future__ import annotations

from typing import Protocol, TypedDict


class StringConvertible(Protocol):
    def __str__(self) -> str:
        pass


class Message(TypedDict):
    role: str
    content: str
