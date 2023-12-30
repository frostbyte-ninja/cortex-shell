from __future__ import annotations

from .irenderer import IRenderer


class NoneRenderer(IRenderer):
    def __enter__(self) -> None:
        pass

    def __exit__(self, *args: object) -> None:
        pass

    def __call__(self, text: str, chunk: str) -> None:
        pass
