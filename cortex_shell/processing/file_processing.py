from __future__ import annotations

from typing import TYPE_CHECKING

from ..history.volatile_history import VolatileHistory
from ..post_processing.no_post_processing import NoPostProcessing
from ..role import FILE_ROLE
from ..types import Message
from .iprocessing import IProcessing

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from ..configuration.schema import Role
    from ..history.ihistory import IHistory
    from ..post_processing.ipost_processing import IPostProcessing


class FileProcessing(IProcessing):
    def __init__(
        self,
        role: Role,
        files: list[Path],
        history: IHistory | None = None,
        post_processing: IPostProcessing | None = None,
    ) -> None:
        self._role = role
        self._files = files
        self._history = history or VolatileHistory()
        self._post_processing = post_processing or NoPostProcessing()
        self._files_added_to_history = False

    def get_messages(self, prompt: str) -> list[Message]:
        messages = self._history.messages()

        if not self._files_added_to_history or not messages:
            messages.append({"role": "system", "content": FILE_ROLE})
            messages.extend(self._files_to_user_message())
            messages.append({"role": "system", "content": self._role.description})
            # files must be ignored after they have been processing, or they will add up because of history
            self._files_added_to_history = True

        messages.append({"role": "user", "content": prompt})

        return messages

    def postprocessing(self, messages: list[Message]) -> None:
        self._history.process_messages(messages)
        self._post_processing(messages)

    def print_history(self) -> None:
        pass

    def _files_to_user_message(self) -> list[Message]:
        messages = []
        for file in self._files:
            content = file.read_text(encoding="utf-8")
            messages.append(Message(role="user", content=f'"{file.name}":\n---\n\n{content}'))

        return messages
