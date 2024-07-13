import functools

import pytest
from prompt_toolkit import PromptSession
from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from cortex_shell.handlers.default_handler import DefaultHandler
from cortex_shell.handlers.repl_handler import ReplHandler

_ctrl_c = b"\x03"
_ctrl_d = b"\x04"
_ctrl_e = b"\x05"


@pytest.fixture
def mock_input():
    with create_pipe_input() as pipe_input, create_app_session(input=pipe_input, output=DummyOutput()):
        pipe_input.send_ctrl_c = functools.partial(pipe_input.send_bytes, _ctrl_c)
        yield pipe_input


@pytest.fixture
def repl_handler(mock_client, mock_processing, mock_renderer, mocker, mock_input):
    handler = ReplHandler(mock_client, mock_processing, mock_renderer)
    mocker.patch.object(handler, "_client")

    session = PromptSession(
        input=mock_input,
        output=DummyOutput(),
    )
    mocker.patch.object(handler, "_prompt_session", session)
    return handler


class TestReplHandler:
    def test_repl_handler_instance(self, repl_handler):
        assert isinstance(repl_handler, DefaultHandler)

    def test_handle_calls_processing_print_history(self, repl_handler, mock_input, mock_processing, mocker):
        mock_super_handle = mocker.patch.object(DefaultHandler, "handle")

        mock_input.send_bytes(_ctrl_c)

        with pytest.raises(KeyboardInterrupt):
            repl_handler.handle("test prompt")

        mock_processing.print_history.assert_called_once()
        mock_super_handle.assert_not_called()

    def test_handle_calls_super_handle(self, repl_handler, mock_input, mock_processing, mocker):
        mock_super_handle = mocker.patch.object(DefaultHandler, "handle")

        mock_input.send_text("command1\n")
        mock_input.send_bytes(_ctrl_c)

        with pytest.raises(KeyboardInterrupt):
            repl_handler.handle("test prompt")

        mock_super_handle.assert_called_once_with("test prompt\n\ncommand1")

    def test_handle_calls_prompt_until_abort(self, repl_handler, mock_input, mock_processing, mocker):
        mock_super_handle = mocker.patch.object(DefaultHandler, "handle")

        mock_input.send_text("command1\n")
        mock_input.send_text("command2\n")
        mock_input.send_bytes(_ctrl_c)

        with pytest.raises(KeyboardInterrupt):
            repl_handler.handle("test prompt")

        assert mock_super_handle.call_count == 2
        assert mock_super_handle.call_args_list[0].args[0] == "test prompt\n\ncommand1"
        assert mock_super_handle.call_args_list[1].args[0] == "command2"

    def test_get_user_input_multiline_toggle(self, repl_handler, mock_input):
        assert repl_handler._multiline is False

        mock_input.send_bytes(_ctrl_e)
        mock_input.send_bytes(_ctrl_c)

        with pytest.raises(KeyboardInterrupt):
            repl_handler.handle("test prompt")

        assert repl_handler._multiline is True

    def test_get_user_input_ctrl_d_handling(self, repl_handler, mock_input, mocker):
        mock_super_handle = mocker.patch.object(DefaultHandler, "handle")

        mock_input.send_text("text in single line mode")  # some text in single line mode which gets discarded
        mock_input.send_bytes(_ctrl_e)  # enable multi line mode
        mock_input.send_text("text\n1234")  # enter multi line prompt
        mock_input.send_bytes(_ctrl_d)  # handle input
        mock_input.send_bytes(_ctrl_c)

        with pytest.raises(KeyboardInterrupt):
            repl_handler.handle("test prompt")

        mock_super_handle.assert_called_once_with("test prompt\n\ntext\n1234")
