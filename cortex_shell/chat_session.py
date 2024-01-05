from __future__ import annotations

from typing import TYPE_CHECKING, Any

import typer

from .configuration import cfg
from .util import option_callback, rmtree
from .yaml import yaml_dump, yaml_load

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from .role import Role
    from .types import Message


class ChatSession:
    def __init__(self, chat_id: str, size: int, storage_path: Path):
        self._chat_id = chat_id
        self._size = size
        self._storage_path = storage_path
        self._storage_path.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        return bool(self._chat_id) and bool(self.get_messages())

    def delete(
        self,
    ) -> None:
        self._get_chat_file_path().unlink(missing_ok=True)

    def to_list(self) -> list[Path]:
        # Get all files in the folder.
        files = self._storage_path.glob("*.yaml")
        # Sort files by last modification time in ascending order.
        return sorted(files, key=lambda f: f.stat().st_mtime)

    def get_messages(self) -> list[Message]:
        content = self._yaml_load()

        if isinstance(content, dict):
            messages = content.get("messages")
            if isinstance(messages, list):
                return messages

        return []

    def write_messages(self, messages: list[Message]) -> None:
        self._write("messages", messages[-self._size :])

    def get_role_name(self) -> str | None:
        return self._read("role")

    def set_role(self, role: Role) -> None:
        self._write("role", role.name)
        self._write("system_prompt", role.description)

    def get_system_prompt(self) -> str:
        return self._read("system_prompt") or ""

    def _get_chat_file_path(self) -> Path:
        return (self._storage_path / self._chat_id).with_suffix(".yaml")

    def _write(self, key: str, value: Any) -> None:
        file_path = self._get_chat_file_path()
        data = self._yaml_load() if file_path.exists() else {}
        data[key] = value

        self._yaml_dump(data)

    def _read(self, key: str) -> Any | None:
        data = self._yaml_load()
        return data.get(key) if data else None

    def _yaml_load(self) -> Any:
        file = self._get_chat_file_path()
        if not file.exists():
            return None
        return yaml_load(self._get_chat_file_path().open("r", encoding="utf-8"))

    def _yaml_dump(self, data: Any) -> Any:
        yaml_dump(data, self._get_chat_file_path().open("w", encoding="utf-8"))

    @classmethod
    @option_callback
    def list_ids_callback(cls, chat_id: str) -> None:
        chat_session = ChatSession(chat_id, cfg().chat_history_size(), cfg().chat_history_path())
        cls.list_ids(chat_session)

    @classmethod
    def list_ids(cls, chat_session: ChatSession) -> None:
        for chat_id in chat_session.to_list():
            typer.echo(chat_id)

    @classmethod
    @option_callback
    def show_messages_callback(cls, chat_id: str) -> None:
        chat_session = ChatSession(chat_id, cfg().chat_history_size(), cfg().chat_history_path())
        cls.show_messages(chat_session)

    @classmethod
    def show_messages(cls, chat_session: ChatSession) -> None:
        for message in chat_session.get_messages():
            role = message["role"]
            if role == "user":
                color = "green"
            elif role == "assistant":
                color = "magenta"
            else:
                color = "yellow"
            typer.secho(f"{role}: " + message["content"], fg=color)

    @classmethod
    @option_callback
    def delete_messages_callback(cls, chat_id: str) -> None:
        chat_session = ChatSession(chat_id, cfg().chat_history_size(), cfg().chat_history_path())
        chat_session.delete()

    @classmethod
    def delete_messages(cls, chat_session: ChatSession) -> None:
        chat_session.delete()

    @classmethod
    @option_callback
    def clear_chats_callback(cls, *_args: Any) -> None:
        rmtree(cfg().chat_history_path())
