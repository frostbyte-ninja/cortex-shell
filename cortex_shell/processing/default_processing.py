from __future__ import annotations

from typing import TYPE_CHECKING

from ..history.volatile_history import VolatileHistory
from ..post_processing.no_post_processing import NoPostProcessing
from .iprocessing import IProcessing

if TYPE_CHECKING:  # pragma: no cover
    from ..configuration.schema import Role
    from ..history.ihistory import IHistory
    from ..post_processing.ipost_processing import IPostProcessing
    from ..types import Message


class DefaultProcessing(IProcessing):
    def __init__(
        self,
        role: Role,
        history: IHistory | None = None,
        post_processing: IPostProcessing | None = None,
    ) -> None:
        self._role = role
        self._history = history or VolatileHistory()
        self._post_processing = post_processing or NoPostProcessing()

    def get_messages(self, prompt: str) -> list[Message]:
        messages = self._history.messages()
        if not messages:
            messages = [{"role": "system", "content": self._role.description}]
        messages.append({"role": "user", "content": prompt})

        return messages

    def postprocessing(self, messages: list[Message]) -> None:
        self._history.process_messages(messages)
        self._post_processing(messages)

    def print_history(self) -> None:
        self._history.print_history()
