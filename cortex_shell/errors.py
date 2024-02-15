from __future__ import annotations

from typing import TYPE_CHECKING

from click import UsageError
from openai import APIError

if TYPE_CHECKING:  # pragma: no cover
    from pydantic import ValidationError


class InvalidConfigError(UsageError):
    def __init__(self, validation_error: ValidationError) -> None:
        errors = validation_error.errors()
        output = [f"{len(errors)} configuration errors"]
        for error in errors:
            location = ".".join(map(str, error["loc"]))
            output.append(f"{location}: {error['msg']}")
        super().__init__(message="\n".join(output))


class FatalError(Exception):
    pass


class ApiError(FatalError):
    code: str | None

    def __init__(self, error: APIError | str) -> None:
        self.code = None

        if isinstance(error, APIError):
            if error.body and isinstance(error.body, dict):
                message = error.body.get("message", "Unknown")
                self.code = error.body.get("code", None)
            elif error.message:
                message = error.message
            else:
                message = "Unknown"
        else:
            message = error

        if self.code:
            message = f"[{self.code}] - {message}"

        super().__init__(message)


class RequestTimeoutError(FatalError):
    pass
