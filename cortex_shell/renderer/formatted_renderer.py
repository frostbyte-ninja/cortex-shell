from __future__ import annotations

from typing import TYPE_CHECKING

from rich.live import Live
from rich.markdown import Markdown
from typing_extensions import Self

from .irenderer import IRenderer

if TYPE_CHECKING:  # pragma: no cover
    from ..configuration.schema import Role


class FormattedRenderer(IRenderer):
    def __init__(self, role: Role) -> None:
        super().__init__()
        self._role = role
        self._live: Live | None = None

    def __enter__(self) -> Self:
        # A new Live object must be created so that we can start with a fresh cursor offset
        self._live = Live(vertical_overflow="visible", auto_refresh=False)
        self._live.__enter__()
        return self

    def __exit__(self, *args: object) -> None:
        self._live.__exit__(*args)
        self._live = None

    def __call__(self, text: str, chunk: str) -> None:
        if self._live is None:
            raise RuntimeError("Renderer must be used as a context manager")

        text += chunk

        self._live.update(
            Markdown(
                text,
                code_theme=self._role.output.theme,
                style=f"bold {self._role.output.color}",
            ),
            refresh=self._role.output.stream,
        )
