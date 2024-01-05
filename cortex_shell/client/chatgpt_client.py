from __future__ import annotations

from typing import TYPE_CHECKING, cast

from openai import AuthenticationError, AzureOpenAI, OpenAI
from openai.types.chat import ChatCompletionMessageParam

from .. import errors
from .base_client import BaseClient

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Generator

    from ..types import Message


class ChatGptClient(BaseClient):
    def __init__(
        self,
        api_key: str,
        timeout: int,
        azure_endpoint: str | None = None,
        azure_deployment: str | None = None,
    ) -> None:
        super().__init__()
        self._api_key = api_key
        self._azure_endpoint = azure_endpoint
        self._azure_deployment = azure_deployment
        self._timeout = timeout

    def _request(
        self,
        messages: list[Message],
        model: str,
        temperature: float,
        top_probability: float,
        stream: bool,
    ) -> Generator[str, None, None]:
        if not self._api_key:
            raise errors.AuthenticationError("Invalid OpenAI API key")

        try:
            if self._azure_endpoint:
                client = AzureOpenAI(
                    api_key=self._api_key,
                    timeout=self._timeout,
                    api_version="2023-09-01-preview",
                    azure_endpoint=self._azure_endpoint,
                    azure_deployment=self._azure_deployment,
                )
            else:
                client = OpenAI(api_key=self._api_key, timeout=self._timeout)

            response = client.chat.completions.create(
                messages=cast(list[ChatCompletionMessageParam], messages),
                model=model,
                temperature=temperature,
                top_p=top_probability,
                stream=stream,
            )
        except AuthenticationError as ex:
            raise errors.AuthenticationError("OpenAI authentication error") from ex

        if stream:
            for chunk in response:
                yield chunk.choices[0].delta.content or ""
        else:
            yield response.choices[0].message.content
