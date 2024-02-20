from abc import abstractmethod
from collections.abc import Generator

from ..cache import Cache
from ..configuration import cfg
from ..types import Message
from .iclient import IClient


class BaseClient(IClient):
    def __init__(self) -> None:
        self._cache = Cache(cfg().config.misc.session.chat_cache_size, cfg().config.misc.session.chat_cache_path)

    def get_completion(
        self,
        messages: list[Message],
        model: str,
        temperature: float,
        top_probability: float,
        stream: bool,
        caching: bool,
    ) -> Generator[str, None, None]:
        yield from self._cache(self._request)(
            messages=messages,
            model=model,
            temperature=temperature,
            top_probability=top_probability,
            stream=stream,
            caching=caching,
        )

    @abstractmethod
    def _request(
        self,
        messages: list[Message],
        model: str,
        temperature: float,
        top_probability: float,
        stream: bool,
    ) -> Generator[str, None, None]:
        raise NotImplementedError
