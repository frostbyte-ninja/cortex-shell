from __future__ import annotations

from typing import TYPE_CHECKING

from rich.live import Live
from rich.markdown import Markdown

from .irenderer import IRenderer

# mypy: disable-error-code="union-attr"

if TYPE_CHECKING:  # pragma: no cover
    from ..role import Role


class FormattedRenderer(IRenderer):
    def __init__(self, role: Role) -> None:
        super().__init__()
        self._role = role

    def __enter__(self) -> None:
        # A new Live object must be created so that we can start with a fresh cursor offset
        self._live = Live(vertical_overflow="visible", auto_refresh=False)
        self._live.__enter__()

    def __exit__(self, *args: object) -> None:
        self._live.__exit__(*args)

    def __call__(self, text: str, chunk: str) -> None:
        text += chunk

        self._live.update(
            Markdown(
                text,
                code_theme=self._role.output.theme,
                style=f"bold {self._role.output.color}",
            ),
            refresh=self._role.output.stream,
        )
