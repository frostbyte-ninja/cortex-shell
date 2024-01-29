from __future__ import annotations

import contextlib
import os.path
import sys
import traceback
from typing import IO, TYPE_CHECKING, Any

from click import ClickException

from . import constants as C  # noqa: N812
from .errors import FatalError

if TYPE_CHECKING:  # pragma: no cover
    from types import TracebackType


class ErrorHandler:
    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if exc_type is None:
            return True

        if (
            exc_type.__module__ == "click.exceptions"
            or issubclass(exc_type, KeyboardInterrupt)
            or issubclass(exc_type, ClickException)
        ):
            # those are handled by click
            return False

        if issubclass(exc_type, FatalError):
            msg, ret_code = "An error has occurred", 1
        else:
            msg, ret_code = "An unexpected error has occurred", 3
        formatted = "".join(traceback.format_exception(exc_type, exc_value, tb))
        self._log_and_exit(msg, ret_code, exc_value, formatted)
        return True

    @staticmethod
    def _log_and_exit(
        msg: str,
        ret_code: int,
        exc: BaseException | None,
        formatted: str,
    ) -> None:
        error_msg = f"{msg}: {type(exc).__name__}: ".encode() + ErrorHandler._force_bytes(exc) if exc else msg.encode()

        with contextlib.ExitStack():
            ErrorHandler._write_line("### version information")
            ErrorHandler._write_line()
            ErrorHandler._write_line("```")
            ErrorHandler._write_line(f"{C.PROJECT_NAME} version: {C.VERSION}")
            ErrorHandler._write_line("sys.version:")
            for line in sys.version.splitlines():
                ErrorHandler._write_line(f"    {line}")
            ErrorHandler._write_line(f"sys.executable: {sys.executable}")
            ErrorHandler._write_line(f"os.name: {os.name}")
            ErrorHandler._write_line(f"sys.platform: {sys.platform}")
            ErrorHandler._write_line("```")
            ErrorHandler._write_line()

            ErrorHandler._write_line("### error information")
            ErrorHandler._write_line()
            ErrorHandler._write_line("```")
            ErrorHandler._write_line_b(error_msg)
            ErrorHandler._write_line("```")
            ErrorHandler._write_line()
            ErrorHandler._write_line("```")
            ErrorHandler._write_line(formatted.rstrip())
            ErrorHandler._write_line("```")
        raise SystemExit(ret_code)

    @staticmethod
    def _write_line_b(s: bytes | None = None, stream: IO[bytes] = sys.stdout.buffer) -> None:
        with contextlib.ExitStack():
            if s is not None:
                stream.write(s)
            stream.write(b"\n")
            stream.flush()

    @staticmethod
    def _write_line(s: str | None = None, **kwargs: Any) -> None:
        ErrorHandler._write_line_b(s.encode() if s is not None else s, **kwargs)

    @staticmethod
    def _force_bytes(exc: Any) -> bytes:
        with contextlib.suppress(TypeError):
            return bytes(exc)
        with contextlib.suppress(Exception):
            return str(exc).encode()
        return f"<unprintable {type(exc).__name__} object>".encode()
