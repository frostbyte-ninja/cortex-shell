from __future__ import annotations

from typing import TYPE_CHECKING

from .ipost_processing import IPostProcessing

if TYPE_CHECKING:  # pragma: no cover
    from ..types import Message


class NoPostProcessing(IPostProcessing):
    def __call__(self, messages: list[Message]) -> None:
        pass
