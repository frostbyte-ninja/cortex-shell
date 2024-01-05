import pytest

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.handlers.default_handler import DefaultHandler
from cortex_shell.post_processing.shell_execution_post_processing import Option, ShellExecutionPostProcessing
from cortex_shell.types import Message
from testing.util import ignore_if_windows


@pytest.fixture()
def messages():
    return [
        Message(role="role1", content="Message 1"),
        Message(role="role2", content="Message 2"),
        Message(role="role3", content="Message 3"),
    ]


@pytest.fixture()
def shell_execution_post_processing(mock_role, mock_shell_role, mock_client):
    return ShellExecutionPostProcessing(shell_role=mock_shell_role, describe_shell_role=mock_role, client=mock_client)


@pytest.fixture()
def mock_prompt(mocker, shell_execution_post_processing):
    return mocker.patch.object(shell_execution_post_processing, "_prompt")


class TestShellExecutionPostProcessing:
    @pytest.mark.usefixtures("_stdin")
    def test_shell_execution_post_processing_abort(
        self,
        shell_execution_post_processing,
        mock_prompt,
        messages,
        mocker,
    ):
        mock_prompt.return_value = Option.ABORT
        run_command_mock = mocker.patch(
            f"{C.PROJECT_MODULE}.post_processing.shell_execution_post_processing.run_command",
        )

        shell_execution_post_processing(messages)

        run_command_mock.assert_not_called()

    @pytest.mark.usefixtures("_no_stdin")
    def test_shell_execution_post_processing_execute(
        self,
        shell_execution_post_processing,
        mock_prompt,
        messages,
        mocker,
    ):
        mock_prompt.return_value = Option.EXECUTE
        run_command_mock = mocker.patch(
            f"{C.PROJECT_MODULE}.post_processing.shell_execution_post_processing.run_command",
        )

        shell_execution_post_processing(messages)

        run_command_mock.assert_called_once_with("Message 3")

    @pytest.mark.usefixtures("_no_stdin")
    def test_shell_execution_post_processing_describe(
        self,
        messages,
        shell_execution_post_processing,
        mock_prompt,
        mock_role,
        mocker,
    ):
        mock_prompt.side_effect = [Option.DESCRIBE, Option.ABORT]
        handle_mock = mocker.patch(
            f"{C.PROJECT_MODULE}.post_processing.shell_execution_post_processing.DefaultHandler.handle",
        )

        shell_execution_post_processing(messages)

        handle_mock.assert_called_once_with(
            "Message 3",
            model=mock_role.options.model,
            temperature=mock_role.options.temperature,
            top_probability=mock_role.options.top_probability,
            stream=mock_role.output.stream,
            caching=False,
        )

    @ignore_if_windows
    @pytest.mark.parametrize(
        ("selected_option", "expected_result"),
        [
            (Option.EXECUTE, Option.EXECUTE),
            (Option.DESCRIBE, Option.DESCRIBE),
            (Option.ABORT, Option.ABORT),
        ],
    )
    def test_prompt_options(self, selected_option, expected_result, mocker):
        mock = mocker.patch("prompt_toolkit.Application.run")
        mock.return_value = selected_option

        shell_execution_post_processing = ShellExecutionPostProcessing(
            shell_role=mocker.Mock(),
            describe_shell_role=mocker.Mock(),
            client=mocker.Mock(),
        )
        result = shell_execution_post_processing._prompt()

        assert result == expected_result

    def test_get_shell_describe_handler(self, mocker):
        mock_shell_role = mocker.Mock()
        mock_describe_shell_role = mocker.Mock()
        mock_client = mocker.Mock()

        shell_execution_post_processing = ShellExecutionPostProcessing(
            shell_role=mock_shell_role,
            describe_shell_role=mock_describe_shell_role,
            client=mock_client,
        )

        handler = shell_execution_post_processing._get_shell_describe_handler(mock_client)

        assert isinstance(handler, DefaultHandler)
        assert handler._processing._role == mock_describe_shell_role
