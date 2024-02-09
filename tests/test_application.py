from typing import Any

import pytest
import typer
from click.testing import Result
from typer.testing import CliRunner

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.application import Application
from testing.util import all_combinations


@pytest.fixture()
def app(mocker, mock_client, monkeypatch):
    monkeypatch.setenv("TERM", "dumb")  # disable colored output
    mocker.patch(f"{C.PROJECT_MODULE}.application.Application._get_client", new=mock_client)

    def invoke_app(prompt: str = "", **kwargs: Any) -> Result:
        app = typer.Typer()
        app.command()(Application)

        arguments = [prompt]
        for key, value in kwargs.items():
            arguments.append(key)
            if isinstance(value, bool):
                continue
            arguments.append(value)
        arguments.insert(0, "--no-cache")
        return CliRunner().invoke(app, arguments)

    return invoke_app


class TestInputs:
    @pytest.mark.usefixtures("_no_stdin")
    def test_no_input(self, app, mocker):
        mock = mocker.patch(f"{C.PROJECT_MODULE}.application.ReplHandler")

        result = app()

        assert result.exit_code == 0
        mock.assert_called_once()

    @pytest.mark.usefixtures("_no_stdin")
    def test_prompt_only(self, app, mocker):
        mock = mocker.patch(f"{C.PROJECT_MODULE}.application.DefaultHandler")

        result = app(prompt="prompt_input")

        assert result.exit_code == 0
        mock.assert_called_once()

    @pytest.mark.usefixtures("_stdin")
    def test_stdin_only(self, app, mocker):
        mock = mocker.patch(f"{C.PROJECT_MODULE}.application.DefaultHandler")

        result = app()

        assert result.exit_code == 0
        mock.assert_called_once()

    @pytest.mark.usefixtures("_no_stdin")
    def test_editor_only(self, app, mocker):
        mock_handler = mocker.patch(f"{C.PROJECT_MODULE}.application.DefaultHandler")
        mock_input = mocker.patch("click.edit", return_value="editor_input")

        result = app(**{"--editor": True})

        assert result.exit_code == 0
        mock_handler.assert_called_once()
        mock_input.assert_called_once()

    @pytest.mark.usefixtures("_no_stdin")
    def test_repl_only(self, app, mocker):
        mock = mocker.patch(f"{C.PROJECT_MODULE}.application.ReplHandler")

        result = app(**{"--repl": True})

        assert result.exit_code == 0
        mock.assert_called_once()

    @pytest.mark.usefixtures("_stdin")
    def test_all_inputs(self, app, mocker):
        mock_handler = mocker.patch(f"{C.PROJECT_MODULE}.application.DefaultHandler")
        mock_input = mocker.patch("click.edit", return_value="editor_input")

        result = app(**{"prompt": "prompt_input", "--editor": True})

        assert result.exit_code == 0
        mock_handler.assert_called_once()
        mock_input.assert_called_once()


class TestValidateOptions:
    def test_roles(self, app):
        combinations = all_combinations(
            {"--role": "some_role"},
            {"--code": True},
            {"--describe-shell": True},
            {"--shell": True},
        )
        for combination in [perm for perm in combinations if len(perm) > 1]:
            result = app(**{k: v for d in combination for k, v in d.items()})

            assert result.exit_code == 2
            assert "Only one of --role, --code, --describe-shell, --shell options" in result.stdout

    def test_repl_with_stdin(self, app):
        result = app(prompt="prompt_input", **{"--repl": True})

        assert result.exit_code == 2
        assert "--repl can not be used with stdin" in result.stdout

    def test_shell_with_output_file(self, app, tmp_dir_factory):
        output_file = tmp_dir_factory.get()

        result = app(prompt="prompt_input", **{"--shell": True, "--output": str(output_file)})

        assert result.exit_code == 2
        assert "Only one of --shell, --output-file options" in result.stdout


class TestConfig:
    def test_no_api_key_error(self):
        app = typer.Typer()
        app.command()(Application)

        result = CliRunner().invoke(app, "prompt_input")

        assert result.exit_code == 1
