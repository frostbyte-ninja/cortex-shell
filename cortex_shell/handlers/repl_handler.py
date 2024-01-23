from __future__ import annotations

from typing import TYPE_CHECKING, Any

import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys

from .default_handler import DefaultHandler

if TYPE_CHECKING:  # pragma: no cover
    from ..client.iclient import IClient
    from ..processing.iprocessing import IProcessing
    from ..renderer.irenderer import IRenderer


class ReplHandler(DefaultHandler):
    def __init__(self, client: IClient, processing: IProcessing, renderer: IRenderer) -> None:
        super().__init__(client, processing, renderer)
        self._prompt_session = PromptSession[str]()
        self._multiline = False

    def handle(self, prompt: str, **kwargs: Any) -> None:  # type: ignore[override]
        self._processing.print_history()

        typer.secho("Entering REPL mode, press Ctrl+C to exit.", fg="yellow")

        self._get_prompt_from_input(prompt, **kwargs)

        while True:
            self._get_prompt_from_input(**kwargs)

    def _get_prompt_from_input(self, additional_prompt: str | None = None, **kwargs: Any) -> None:
        if additional_prompt:
            typer.secho(additional_prompt, fg="green")

        user_input = self._get_user_input()

        prompt = f"{additional_prompt}\n\n{user_input}" if additional_prompt else user_input

        super().handle(prompt, **kwargs)

    def _get_user_input(self) -> Any:
        bindings = KeyBindings()

        @bindings.add(Keys.ControlE)  # type: ignore[misc]
        def _toggle_multiline(event: KeyPressEvent) -> None:
            self._multiline = not self._multiline
            event.app.exit()

        @bindings.add(Keys.ControlD)  # type: ignore[misc]
        def _handle_multiline_input(event: KeyPressEvent) -> None:
            if self._multiline and len(event.current_buffer.text) > 0:
                event.current_buffer.validate_and_handle()

        user_input = ""
        while not user_input:
            user_input = self._prompt_session.prompt(
                ">>> " if self._multiline else "> ",
                multiline=self._multiline,
                key_bindings=bindings,
            )

        return user_input
