from __future__ import annotations

from typing import TYPE_CHECKING, cast

import httpx
from openai import APIConnectionError, APITimeoutError, AuthenticationError, AzureOpenAI, NotFoundError, OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

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
            raise errors.AuthenticationError("No OpenAI API key")

        client = self._get_client()

        try:
            response = client.chat.completions.create(
                messages=cast(list[ChatCompletionMessageParam], messages),
                model=model,
                temperature=temperature,
                top_p=top_probability,
                stream=stream,
            )
        except AuthenticationError as e:
            raise errors.AuthenticationError("OpenAI authentication error") from e
        except NotFoundError as e:
            raise errors.DeploymentNotFoundError(
                f'Chat completion deployment "{self._azure_deployment}" not found on endpoint {self._azure_endpoint}',
            ) from e
        except APITimeoutError as e:
            raise errors.RequestTimeoutError from e
        except APIConnectionError as e:
            raise errors.ConnectError from e

        yield from self._process_response(response, stream)

    def _get_client(self) -> AzureOpenAI | OpenAI:
        if self._azure_endpoint:
            return AzureOpenAI(
                api_key=self._api_key,
                timeout=self._timeout,
                api_version="2023-09-01-preview",
                azure_endpoint=self._azure_endpoint,
                azure_deployment=self._azure_deployment,
            )
        else:
            return OpenAI(api_key=self._api_key, timeout=self._timeout)

    @staticmethod
    def _process_response(response: Stream | ChatCompletion, stream: bool) -> Generator[str, None, None]:
        try:
            if stream:
                for chunk in response:
                    yield chunk.choices[0].delta.content or "" if chunk.choices else ""
            else:
                yield response.choices[0].message.content or "" if response.choices else ""
        except httpx.ReadTimeout as e:
            raise errors.RequestTimeoutError from e
