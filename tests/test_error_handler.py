from __future__ import annotations

import functools
import io

import pytest
import re_assert

import cortex_shell
from cortex_shell import constants as C  # noqa: N812
from cortex_shell.error_handler import ErrorHandler
from cortex_shell.errors import FatalError


@pytest.fixture
def error_handler():
    return ErrorHandler()


@pytest.fixture
def mock_log_and_exit(mocker, error_handler):
    return mocker.patch.object(error_handler, "_log_and_exit")


@pytest.fixture
def capture_output(mocker, error_handler):
    class FakeStream:
        def __init__(self) -> None:
            self.data = io.BytesIO()

        def write(self, s):
            self.data.write(s)

        def flush(self):
            pass

    class StreamWrapper:
        def __init__(self, stream) -> None:
            self._stream = stream

        def get_bytes(self):
            data = self._stream.data.getvalue()
            self._stream.data.seek(0)
            self._stream.data.truncate()
            return data.replace(b"\r\n", b"\n")

        def get(self):
            return self.get_bytes().decode()

    fake_stream = FakeStream()
    write_line_b = functools.partial(error_handler._write_line_b, stream=fake_stream)
    mocker.patch.object(cortex_shell.error_handler.ErrorHandler, "_write_line_b", write_line_b)
    return StreamWrapper(fake_stream)


class TestErrorHandler:
    def test_error_handler_no_exception(self, error_handler, mock_log_and_exit):
        with error_handler:
            pass
        assert mock_log_and_exit._log_and_exit.call_count == 0

    def test_fatal_error(self, mocker, error_handler, mock_log_and_exit):
        exc = FatalError("just a test")
        with error_handler:
            raise exc

        mock_log_and_exit.assert_called_once_with(
            "An error has occurred",
            1,
            exc,
            mocker.ANY,
        )

        pattern = re_assert.Matches(
            rf"Traceback \(most recent call last\):\n"
            rf'  File ".+tests.test_error_handler.py", line \d+, in test_fatal_error\n'
            rf"    raise exc\n"
            rf"({C.PROJECT_MODULE}\.errors\.)?FatalError: just a test\n",
        )
        pattern.assert_matches(mock_log_and_exit.call_args[0][3])

    def test_unexpected_error(self, mocker, error_handler, mock_log_and_exit):
        exc = ValueError("another test")
        with error_handler:
            raise exc

        mock_log_and_exit.assert_called_once_with(
            "An unexpected error has occurred",
            3,
            exc,
            mocker.ANY,
        )
        pattern = re_assert.Matches(
            r"Traceback \(most recent call last\):\n"
            r'  File ".+tests.test_error_handler.py", line \d+, in test_unexpected_error\n'
            r"    raise exc\n"
            r"ValueError: another test\n",
        )
        pattern.assert_matches(mock_log_and_exit.call_args[0][3])

    def test_keyboard_interrupt(self, error_handler, mock_log_and_exit):
        with pytest.raises(KeyboardInterrupt), error_handler:
            raise KeyboardInterrupt

        mock_log_and_exit.assert_not_called()

    def test_error_handler_non_ascii_exception(self, error_handler):
        with pytest.raises(SystemExit), error_handler:
            raise ValueError("☃")

    def test_error_handler_non_stringable_exception(self, error_handler):
        class TestError(Exception):
            def __str__(self) -> str:
                raise RuntimeError("not today!")

        with pytest.raises(SystemExit), error_handler:
            raise TestError

    def test_log_and_exit(self, error_handler, capture_output):
        tb = (
            f"Traceback (most recent call last):\n"
            f'  File "<stdin>", line 2, in <module>\n'
            f"{C.PROJECT_MODULE}.errors.FatalError: abc\n"
        )

        with pytest.raises(SystemExit) as exc_info:
            error_handler._log_and_exit("msg", 1, FatalError("abc"), tb)
        assert exc_info.value.code == 1

        pattern = re_assert.Matches(
            rf"^### version information\n"
            rf"\n"
            rf"```\n"
            rf"{C.PROJECT_NAME} version: \d+\.\d+\.\d+\n"
            rf"sys.version:\n"
            rf"(    .*\n)*"
            rf"sys.executable: .*\n"
            rf"os.name: .*\n"
            rf"sys.platform: .*\n"
            rf"```\n"
            rf"\n"
            rf"### error information\n"
            rf"\n"
            rf"```\n"
            rf"msg: FatalError: abc\n"
            rf"```\n"
            rf"\n"
            rf"```\n"
            rf"Traceback \(most recent call last\):\n"
            rf'  File "<stdin>", line 2, in <module>\n'
            rf"{C.PROJECT_MODULE}\.errors\.FatalError: abc\n"
            rf"```\n",
        )

        pattern.assert_matches(capture_output.get())
