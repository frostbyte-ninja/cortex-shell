from __future__ import annotations

from typing import TYPE_CHECKING

from .ihandler import IHandler

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Generator
    from typing import Any

    from ..client.iclient import IClient
    from ..processing.iprocessing import IProcessing
    from ..renderer.irenderer import IRenderer


class DefaultHandler(IHandler):
    def __init__(self, client: IClient, processing: IProcessing, renderer: IRenderer) -> None:
        self._client = client
        self._processing = processing
        self._renderer = renderer

    def get_completion(self, **kwargs: Any) -> Generator[str, None, None]:
        yield from self._client.get_completion(**kwargs)

    def handle(self, prompt: str, **kwargs: Any) -> str:
        messages = self._processing.get_messages(prompt)

        full_response = ""
        with self._renderer:
            for chunk in self.get_completion(messages=messages, **kwargs):
                self._renderer(full_response, chunk)
                full_response += chunk

        messages.append({"role": "assistant", "content": full_response})
        self._processing.postprocessing(messages)

        return full_response
