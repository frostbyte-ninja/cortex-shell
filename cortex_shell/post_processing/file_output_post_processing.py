from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from ..types import Message

from .ipost_processing import IPostProcessing


class FileOutputPostProcessing(IPostProcessing):
    def __init__(self, file: Path) -> None:
        self._file = file

    def __call__(self, messages: list[Message]) -> None:
        current_assistant_message = messages[-1]["content"]
        self._file.write_text(current_assistant_message, encoding="utf-8")
