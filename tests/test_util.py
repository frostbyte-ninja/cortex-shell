from __future__ import annotations

import stat
import subprocess
from unittest.mock import ANY

import pytest
import typer
from pydantic import BaseModel

from cortex_shell import constants as C  # noqa: N812  # noqa: N812
from cortex_shell.util import (
    fill_values,
    get_colored_text,
    get_resource_file,
    option_callback,
    os_name,
    print_formatted_text,
    rmtree,
    run_command,
    shell_name,
)
from testing.util import get_path_to_shell, get_test_resource_file, ignore_if_windows, prepend_dir_to_path


class TestOptionCallback:
    def test_option_callback_with_none_value(self, mocker):
        mock = mocker.Mock()
        decorated_func = option_callback(mock)

        decorated_func(object, None)
        mock.assert_not_called()

    def test_option_callback_with_false(self, mocker):
        mock = mocker.Mock()
        decorated_func = option_callback(mock)

        decorated_func(object, False)
        mock.assert_not_called()

    def test_option_callback_with_empty_string(self, mocker):
        mock = mocker.Mock()
        decorated_func = option_callback(mock)

        decorated_func(object, "")
        mock.assert_not_called()

    def test_option_callback_with_true(self, mocker):
        mock = mocker.Mock()
        decorated_func = option_callback(mock)

        with pytest.raises(typer.Exit):
            decorated_func(object, True)
        mock.assert_called_once_with(object, True)

    def test_option_callback_with_string(self, mocker):
        mock = mocker.Mock()
        decorated_func = option_callback(mock)
        value = "text"

        with pytest.raises(typer.Exit):
            decorated_func(object, value)
        mock.assert_called_once_with(object, value)


class TestShellIntegration:
    @pytest.mark.parametrize(
        ("shell", "config_file"),
        [
            ("bash", ".bashrc"),
            ("zsh", ".zshrc"),
            ("fish", ".config/fish/config.fish"),
            ("powershell", "Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1"),
            ("pwsh", "Documents/PowerShell/Microsoft.PowerShell_profile.ps1"),
        ],
    )
    def test_shell_integration_installation(self, mocker, tmp_dir_factory, mock_shell_integration, shell, config_file):
        tmp_home = tmp_dir_factory.get()
        mocker.patch("pathlib.Path.home", return_value=tmp_home)
        mocker.patch(f"{C.PROJECT_MODULE}.util.get_powershell_profile_path", return_value=tmp_home / config_file)

        shell_config_path = tmp_home / config_file

        assert not shell_config_path.is_file()

        mock_shell_integration(shell)

        assert shell_config_path.is_file()

        with (
            shell_config_path.open("r") as written_file,
            get_resource_file(shell, "shell_integrations").open(
                "r",
            ) as original_file,
        ):
            original_content = f"# cortex-shell integration\n{original_file.read().strip()}\n# cortex-shell integration"
            written_content = written_file.read()
            assert original_content in written_content

    @pytest.mark.parametrize(
        ("shell", "config_file"),
        [
            ("bash", ".bashrc"),
            ("zsh", ".zshrc"),
            ("fish", ".config/fish/config.fish"),
            ("powershell", "Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1"),
        ],
    )
    def test_shell_integration_update(self, mocker, tmp_dir_factory, mock_shell_integration, shell, config_file):
        tmp_home = tmp_dir_factory.get()
        mocker.patch("pathlib.Path.home", return_value=tmp_home)
        mocker.patch(f"{C.PROJECT_MODULE}.util.get_powershell_profile_path", return_value=tmp_home / config_file)

        shell_config_path = tmp_home / config_file

        mock_shell_integration(shell)

        # There is already an installed integration
        with shell_config_path.open("w") as installed_file:
            installed_file.write(
                "# cortex-shell integration\necho 'Updated shell integration'\n# cortex-shell integration",
            )

        # Test updating the existing integration
        mock_shell_integration(shell)

        with (
            shell_config_path.open("r") as written_file,
            get_resource_file(shell, "shell_integrations").open(
                "r",
            ) as updated_file,
        ):
            updated_content = f"# cortex-shell integration\n{updated_file.read().strip()}\n# cortex-shell integration"
            written_content = written_file.read()
            assert updated_content in written_content

    def test_unsupported_shell(self, mocker, mock_shell_integration):
        mocker.patch(f"{C.PROJECT_MODULE}.util.shell_name", return_value="unsupported_shell")
        mock = mocker.patch("typer.echo")

        mock_shell_integration("unsupported_shell")

        mock.assert_called_once_with('"unsupported_shell" shell is not supported.')

    @ignore_if_windows
    def test_bash(self, mock_shell_integration, mock_executable):
        shell_name = "bash"
        shell_path = get_path_to_shell(shell_name)
        if shell_path is None:
            pytest.skip(f"{shell_name} not found")

        mock_shell_integration(shell_name)

        try:
            output = subprocess.check_output(
                [str(shell_path), get_test_resource_file(shell_name, "shell_integration_wrappers")],
                stderr=subprocess.STDOUT,
                timeout=5,
                env=prepend_dir_to_path(mock_executable.parent),
            ).decode("utf-8")
        except subprocess.CalledProcessError as e:
            output = e.output.decode("utf-8")

        assert output == "COMPLETION"


class TestGetColoredText:
    def test_text(self):
        text = "Hello, World!"
        color = "green"
        expected_result = [("ansigreen bold", "Hello, World!")]
        result = get_colored_text(text, color)
        assert result == expected_result

    def test_text_with_html_characters(self):
        text = "<test>"
        color = "red"
        expected_result = [("ansired bold", "<test>")]
        result = get_colored_text(text, color)
        assert result == expected_result


class TestOsName:
    def test_os_name_linux(self, mocker):
        mocker.patch("platform.system", return_value="Linux")
        mocker.patch("distro.name", return_value="TestDistro")

        result = os_name()
        assert result == "Linux/TestDistro"

    def test_os_name_windows(self, mocker):
        mocker.patch("platform.system", return_value="Windows")
        mocker.patch("platform.release", return_value="10")

        result = os_name()
        assert result == "Windows 10"

    def test_os_name_darwin(self, mocker):
        mocker.patch("platform.system", return_value="Darwin")
        mocker.patch("platform.mac_ver", return_value=("10.15.7", ("", "", ""), ""))

        result = os_name()
        assert result == "Darwin/MacOS 10.15.7"

    def test_os_name_other(self, mocker):
        mocker.patch("platform.system", return_value="Other")

        result = os_name()
        assert result == "Other"


class TestShellName:
    @pytest.mark.parametrize(
        ("os_system", "expected_shell_name"),
        [
            ("Linux", "bash"),
            ("Linux", "zsh"),
            ("Linux", "fish"),
            ("Windows", "powershell"),
            ("Windows", "pwsh"),
            ("Darwin", "bash"),
            ("Darwin", "zsh"),
            ("Darwin", "fish"),
        ],
    )
    def test_shell_name_shell_variable(
        self,
        mocker,
        os_system,
        expected_shell_name,
    ):
        mocker.patch("platform.system", return_value=os_system)
        mocker.patch(f"{C.PROJECT_MODULE}.util.detect_shell", return_value=(expected_shell_name,))

        assert shell_name() == expected_shell_name


class TestRunCommand:
    @pytest.mark.parametrize(
        ("os_system", "shell", "command", "expected_full_command"),
        [
            ("Linux", "bash", "echo Hello, World!", ["bash", "-c", "echo Hello, World!"]),
            ("Linux", "bash", "echo 'Hello, World!'", ["bash", "-c", "echo 'Hello, World!'"]),
            ("Linux", "zsh", "echo Hello, World!", ["zsh", "-c", "echo Hello, World!"]),
            ("Linux", "sh", "echo Hello, World!", ["sh", "-c", "echo Hello, World!"]),
            ("Linux", "ksh", "echo Hello, World!", ["ksh", "-c", "echo Hello, World!"]),
            ("Linux", "fish", "echo Hello, World!", ["fish", "-c", "echo Hello, World!"]),
            ("Linux", "dash", "echo Hello, World!", ["dash", "-c", "echo Hello, World!"]),
            ("Linux", "ash", "echo Hello, World!", ["ash", "-c", "echo Hello, World!"]),
            ("Linux", "csh", "echo Hello, World!", ["csh", "-c", "echo Hello, World!"]),
            ("Linux", "pwsh", "echo Hello, World!", ["pwsh", "-Command", '"echo Hello, World!"']),
            ("Windows", "powershell", "echo Hello, World!", ["powershell", "-Command", '"echo Hello, World!"']),
            ("Windows", "pwsh", "echo Hello, World!", ["pwsh", "-Command", '"echo Hello, World!"']),
            ("Windows", "cmd", "echo Hello, World!", ["cmd", "/c", '"echo Hello, World!"']),
            ("Windows", "bash", "echo Hello, World!", ["bash", "-c", "echo Hello, World!"]),
            ("Windows", "zsh", "echo Hello, World!", ["zsh", "-c", "echo Hello, World!"]),
        ],
    )
    def test_run_command(self, mocker, os_system, shell, command, expected_full_command):
        mocker.patch("platform.system", return_value=os_system)
        mocker.patch(f"{C.PROJECT_MODULE}.util.shell_name", return_value=shell)
        mock = mocker.patch("subprocess.run")

        run_command(command)
        mock.assert_called_once_with(expected_full_command, check=ANY)

    def test_run_command_suppress_called_process_error(self, mocker):
        mocker.patch("platform.system", return_value="Linux")
        mocker.patch(f"{C.PROJECT_MODULE}.util.shell_name", return_value="bash")
        mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "bash -c 'echo Hello, World!'"))

        try:
            run_command("echo 'Hello, World!'")
        except subprocess.CalledProcessError:
            pytest.fail("CalledProcessError should be suppressed")

    def test_run_command_unsupported_shell(self, mocker):
        mocker.patch("platform.system", return_value="Linux")
        mocker.patch(f"{C.PROJECT_MODULE}.util.shell_name", return_value="unsupported_shell")

        # Mock shell_name
        with pytest.raises(ValueError, match="Unsupported shell: unsupported_shell"):
            run_command("echo 'Hello, World!'")


class TestPrintFormattedText:
    def test_print_plain_text_tty(self, mocker):
        mocker.patch(f"{C.PROJECT_MODULE}.util.is_tty", return_value=True)
        print_mock = mocker.patch("builtins.print")
        mock = mocker.patch(f"{C.PROJECT_MODULE}.util.print_formatted_text_orig")

        text1 = "1234"
        text2 = "5678"
        print_formatted_text(text1, text2, sep=": ", end="\t")

        print_mock.assert_not_called()
        mock.assert_called_once_with(text1, text2, sep=": ", end="\t")

    def test_print_formatted_text_tty(self, mocker):
        mocker.patch(f"{C.PROJECT_MODULE}.util.is_tty", return_value=True)
        print_mock = mocker.patch("builtins.print")
        mock = mocker.patch(f"{C.PROJECT_MODULE}.util.print_formatted_text_orig")

        text1 = get_colored_text("1234", "red")
        text2 = get_colored_text("5678", "green")
        print_formatted_text(text1, text2, sep=": ", end="\t")

        print_mock.assert_not_called()
        mock.assert_called_once_with(text1, text2, sep=": ", end="\t")

    def test_print_plain_text_no_tty(self, mocker):
        mocker.patch(f"{C.PROJECT_MODULE}.util.is_tty", return_value=False)
        print_mock = mocker.patch("builtins.print")
        mock = mocker.patch(f"{C.PROJECT_MODULE}.util.print_formatted_text_orig")

        text1 = "1234"
        text2 = "5678"
        print_formatted_text(text1, text2, sep=": ", end="\t")

        print_mock.assert_called_once_with(text1, text2, sep=": ", end="\t")
        mock.assert_not_called()

    def test_print_formatted_text_notty(self, mocker):
        mocker.patch(f"{C.PROJECT_MODULE}.util.is_tty", return_value=False)
        print_mock = mocker.patch("builtins.print")
        mock = mocker.patch(f"{C.PROJECT_MODULE}.util.print_formatted_text_orig")

        text1 = "1234"
        text2 = "5678"
        print_formatted_text(get_colored_text("1234", "red"), get_colored_text("5678", "green"), sep=": ", end="\t")

        print_mock.assert_called_once_with(text1, text2, sep=": ", end="\t")
        mock.assert_not_called()


class TestRmTree:
    def test_rmtree_read_only_directories(self, tmp_path):
        a_dir = tmp_path / "a"
        b_dir = a_dir / "b"
        c_dir = b_dir / "c"
        a_file = c_dir / "a"

        c_dir.mkdir(parents=True, exist_ok=True)
        a_file.touch()

        mode = a_dir.stat().st_mode
        mode_no_w = mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
        c_dir.chmod(mode_no_w)
        b_dir.chmod(mode_no_w)
        a_dir.chmod(mode_no_w)

        rmtree(a_dir)

        assert not a_dir.exists()


class D(BaseModel):
    d1: str | None = "nested"


class B(BaseModel):
    b1: str | None = "hello"
    b2: dict[str, str] | None = {"key": "value"}
    b3: D | None = D()


class A(BaseModel):
    a1: int | None = 1
    a2: list[int] | None = [1, 2, 3]
    a3: B | None = B()


class TestFillValues:
    def test_all_none(self):
        source = A()
        target = A()
        target.a1 = None
        target.a2 = None
        target.a3 = None

        fill_values(source, target)

        assert target == source

    def test_keep_existing_values(self):
        source = A()
        target = A()
        target.a1 = 2
        target.a2 = [4, 5, 6]
        target.a3.b1 = None
        target.a3.b2 = {"abc": "def"}
        target.a3.b3.d1 = "none"

        fill_values(source, target)

        assert target.a1 == 2
        assert target.a2 == [4, 5, 6]
        assert target.a3.b2 == {"abc": "def"}
        assert target.a3.b3.d1 == "none"

    def test_keep_empty_existing_containers(self):
        source = A()
        target = A()
        target.a2 = []
        target.a3.b1 = ""
        target.a3.b2 = {}
        target.a3.b3.d1 = ""

        fill_values(source, target)

        assert target.a2 == []
        assert target.a3.b1 == ""  # noqa: PLC1901
        assert target.a3.b2 == {}
        assert target.a3.b3.d1 == ""  # noqa: PLC1901
