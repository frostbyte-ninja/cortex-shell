from __future__ import annotations

from typing import TYPE_CHECKING, Any

import click
import typer

from ..configuration import cfg
from ..util import option_callback, rmtree
from .chat_session import ChatSession

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path


class ChatSessionManager:
    def __init__(self, storage_path: Path, history_size: int | None = None):
        self._storage_path = storage_path
        self._history_size = history_size
        self._storage_path.mkdir(parents=True, exist_ok=True)

    def get_session(self, chat_id: str) -> ChatSession:
        return ChatSession((self._storage_path / chat_id).with_suffix(".yaml"), self._history_size)

    def as_list(self) -> list[Path]:
        files = self._storage_path.glob("*.yaml")
        return sorted(files, key=lambda f: f.stat().st_mtime)

    def clear_chats(self) -> None:
        rmtree(self._storage_path)

    def print_chats(self) -> None:
        files = self.as_list()
        chat_sessions = []

        for file in files:
            session = ChatSession(file)
            first_user_prompt = next(
                (message["content"] for message in session.messages() if message["role"] == "user"),
                None,
            )
            if first_user_prompt:
                chat_sessions.append((session, first_user_prompt))

        typer.echo("Chats ", nl=False)
        typer.secho(f"({len(chat_sessions)})", nl=False, fg="bright_black")
        typer.echo(":")

        if not chat_sessions:
            typer.echo("No chats found.")
            return

        chat_id_width = max(len(session.chat_id()) for session, _ in chat_sessions) + 1

        for session, first_user_prompt in chat_sessions:
            first_line = first_user_prompt.split("\n", 1)[0]
            typer.secho("• ", nl=False, fg="bright_black")
            typer.echo(f"{session.chat_id():<{chat_id_width}}", nl=False)
            typer.secho(first_line, fg="bright_black")

    @staticmethod
    def print_messages(chat_session: ChatSession) -> None:
        messages = [msg for msg in chat_session.messages() if msg["role"] in {"user", "assistant"}]
        for index, message in enumerate(messages):
            role = message["role"]
            color, prefix = {
                "user": ("green", "Prompt"),
                "assistant": ("magenta", "Response"),
            }[role]

            typer.secho(f"{prefix}:", bold=True, nl=False, fg=color)
            end = "\n" if index != len(messages) - 1 else ""
            typer.secho(f" {message['content']}{end}", fg=color)

    @classmethod
    @option_callback
    def show_chat_callback(cls, chat_id: str) -> None:
        session = cls._get_manager().get_session(chat_id)
        if session.exists():
            cls.print_messages(cls._get_manager().get_session(chat_id))
        else:
            raise click.UsageError(f'Chat with ID "{chat_id}" not found')

    @classmethod
    @option_callback
    def delete_chat_callback(cls, chat_id: str) -> None:
        session = cls._get_manager().get_session(chat_id)
        if session.exists():
            cls._get_manager().get_session(chat_id).delete()
        else:
            raise click.UsageError(f'Chat with ID "{chat_id}" not found')

    @classmethod
    @option_callback
    def list_chats_callback(cls, *_args: Any) -> None:
        cls._get_manager().print_chats()

    @classmethod
    @option_callback
    def clear_chats_callback(cls, *_args: Any) -> None:
        cls._get_manager().clear_chats()

    @staticmethod
    def _get_manager() -> ChatSessionManager:
        return ChatSessionManager(cfg().config.misc.session.chat_history_path)
