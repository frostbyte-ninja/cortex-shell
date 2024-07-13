from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from ..types import YamlType
from ..yaml import yaml_dump, yaml_load

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from ruamel.yaml import StreamType

    from ..types import Message


class ChatSession:
    def __init__(self, file_path: Path, size: int | None = None) -> None:
        self._file_path = file_path
        self._size = size

    def exists(self) -> bool:
        return self._file_path.exists() and bool(self.messages())

    def delete(self) -> None:
        self._file_path.unlink(missing_ok=True)

    def chat_id(self) -> str:
        return self._file_path.stem

    def messages(self) -> list[Message]:
        content = self._yaml_load()

        if isinstance(content, dict):
            messages = content.get("messages")
            if isinstance(messages, list):
                return messages

        return []

    def write_messages(self, messages: list[Message]) -> None:
        if self._size is not None:
            messages = messages[-self._size :]
        self._write("messages", cast(YamlType, messages))

    def _write(self, key: str, value: YamlType) -> None:
        data = self._yaml_load() if self._file_path.exists() else {}
        data[key] = value

        self._yaml_dump(data)

    def _read(self, key: str) -> YamlType:
        data = self._yaml_load()
        if isinstance(data, dict):
            return data.get(key)
        return None

    def _yaml_load(self) -> Any:  # noqa: ANN401
        if not self._file_path.exists():
            return None
        return yaml_load(stream=self._file_path)

    def _yaml_dump(self, data: Path | StreamType) -> Any:  # noqa: ANN401
        yaml_dump(data=data, stream=self._file_path)
