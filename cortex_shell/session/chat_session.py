from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..yaml import yaml_dump, yaml_load

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from ..configuration.schema import Role
    from ..types import Message


class ChatSession:
    def __init__(self, file_path: Path, size: int | None = None):
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
        self._write("messages", messages)

    def get_role_name(self) -> str | None:
        return self._read("role")

    def set_role(self, role: Role) -> None:
        self._write("role", role.name)
        self._write("system_prompt", role.description)

    def get_system_prompt(self) -> str:
        return self._read("system_prompt") or ""

    def _write(self, key: str, value: Any) -> None:
        data = self._yaml_load() if self._file_path.exists() else {}
        data[key] = value

        self._yaml_dump(data)

    def _read(self, key: str) -> Any | None:
        data = self._yaml_load()
        return data.get(key) if data else None

    def _yaml_load(self) -> Any:
        if not self._file_path.exists():
            return None
        return yaml_load(stream=self._file_path)

    def _yaml_dump(self, data: Any) -> Any:
        yaml_dump(data=data, stream=self._file_path)
