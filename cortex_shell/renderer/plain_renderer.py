from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Self

from ..util import get_colored_text, print_formatted_text
from .irenderer import IRenderer

if TYPE_CHECKING:  # pragma: no cover
    from ..configuration.schema import Role


class PlainRenderer(IRenderer):
    def __init__(self, role: Role):
        self._role = role

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        # new line
        print_formatted_text()

    def __call__(self, text: str, chunk: str) -> None:
        print_formatted_text(get_colored_text(chunk, self._role.output.color), end="")  # type: ignore[arg-type]
