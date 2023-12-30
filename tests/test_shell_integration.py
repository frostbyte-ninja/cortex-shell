import subprocess
import sys

import pytest

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.util import get_resource_file
from testing.util import get_path_to_shell, get_test_resource_file, prepend_dir_to_path


class TestShellIntegration:
    @pytest.mark.parametrize(
        ("shell", "config_file"),
        [("bash", ".bashrc"), ("zsh", ".zshrc"), ("fish", ".config/fish/config.fish")],
    )
    def test_shell_integration_installation(self, mocker, tmp_dir_factory, mock_shell_integration, shell, config_file):
        tmp_home = tmp_dir_factory.get()
        mocker.patch("pathlib.Path.home", return_value=tmp_home)
        shell_config_path = tmp_home / config_file

        assert not shell_config_path.is_file()

        mock_shell_integration(shell)

        assert shell_config_path.is_file()

        with shell_config_path.open("r") as written_file, get_resource_file(shell, "shell_integrations").open(
            "r",
        ) as original_file:
            original_content = f"# cortex-shell integration\n{original_file.read().strip()}\n# cortex-shell integration"
            written_content = written_file.read()
            assert original_content in written_content

    @pytest.mark.parametrize(
        ("shell", "config_file"),
        [("bash", ".bashrc"), ("zsh", ".zshrc"), ("fish", ".config/fish/config.fish")],
    )
    def test_shell_integration_update(self, mocker, tmp_dir_factory, mock_shell_integration, shell, config_file):
        tmp_home = tmp_dir_factory.get()
        mocker.patch("pathlib.Path.home", return_value=tmp_home)
        shell_config_path = tmp_home / config_file

        mock_shell_integration(shell)

        # There is already an installed integration
        with shell_config_path.open("w") as installed_file:
            installed_file.write(
                "# cortex-shell integration\necho 'Updated shell integration'\n# cortex-shell integration",
            )

        # Test updating the existing integration
        mock_shell_integration(shell)

        with shell_config_path.open("r") as written_file, get_resource_file(shell, "shell_integrations").open(
            "r",
        ) as updated_file:
            updated_content = f"# cortex-shell integration\n{updated_file.read().strip()}\n# cortex-shell integration"
            written_content = written_file.read()
            assert updated_content in written_content

    def test_unsupported_shell(self, mocker, mock_shell_integration):
        mocker.patch(f"{C.PROJECT_MODULE}.util.shell_name", return_value="unsupported_shell")
        mock = mocker.patch("typer.echo")

        mock_shell_integration("unsupported_shell")

        mock.assert_called_once_with('Your shell "unsupported_shell" is not supported.')

    @pytest.mark.skipif(sys.platform == "win32", reason="does not work reliably on windows")
    def test_bash(self, mock_shell_integration, mock_executable):
        shell_name = "bash"
        shell_path = get_path_to_shell(shell_name)
        if shell_path is None:
            pytest.skip(f"{shell_name} not found")

        mock_shell_integration(shell_name)

        try:
            output = subprocess.check_output(
                [shell_path, get_test_resource_file(shell_name, "shell_integration_wrappers")],
                stderr=subprocess.STDOUT,
                timeout=5,
                env=prepend_dir_to_path(mock_executable.parent),
            )
        except subprocess.CalledProcessError as e:
            output = e.output

        output = output.decode("utf-8")

        assert str(output) == "COMPLETION"
