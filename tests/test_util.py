import stat
import subprocess

import pytest

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.util import get_colored_text, os_name, rmtree, run_command, shell_name


class MockProcess:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

    def parent(self):
        return self


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
    def test_shell_name_from_process(self, mocker, monkeypatch):
        monkeypatch.delenv("SHELL", raising=False)
        mocker.patch("platform.system", return_value="Linux")
        mocker.patch("psutil.Process", return_value=MockProcess("bash"))

        assert shell_name() == "bash"

    @pytest.mark.parametrize(
        ("process_name", "expected_shell_name"),
        [
            ("pwsh", "powershell"),
            ("pwsh.exe", "powershell"),
            ("powershell.exe", "powershell"),
        ],
    )
    def test_shell_name_powershell(self, mocker, process_name, expected_shell_name, monkeypatch):
        monkeypatch.delenv("SHELL", raising=False)
        mocker.patch("platform.system", return_value="Windows")
        mocker.patch("psutil.Process", return_value=MockProcess(process_name))

        assert shell_name() == expected_shell_name

    def test_shell_name_cmd(self, mocker, monkeypatch):
        monkeypatch.delenv("SHELL", raising=False)
        mocker.patch("platform.system", return_value="Windows")
        mocker.patch("psutil.Process", return_value=MockProcess("cmd.exe"))

        assert shell_name() == "cmd"

    @pytest.mark.parametrize(
        ("os_system", "shell_env", "process_name", "expected_shell_name"),
        [
            ("Linux", r"/bin/bash", "bash", "bash"),
            ("Linux", r"/usr/local/bin/zsh", "zsh", "zsh"),
            ("Linux", r"/usr/bin/fish", "fish", "fish"),
            ("Windows", r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", "powershell.exe", "powershell"),
            ("Windows", r"C:\Program Files\PowerShell\7\pwsh.exe", "pwsh.exe", "powershell"),
            ("Darwin", r"/bin/bash", "bash", "bash"),
            ("Darwin", r"/usr/local/bin/zsh", "zsh", "zsh"),
            ("Darwin", r"/usr/local/bin/fish", "fish", "fish"),
        ],
    )
    def test_shell_name_shell_variable(
        self,
        mocker,
        os_system,
        shell_env,
        process_name,
        expected_shell_name,
        monkeypatch,
    ):
        monkeypatch.delenv("SHELL", raising=False)
        mocker.patch("platform.system", return_value=os_system)
        mocker.patch("psutil.Process", return_value=MockProcess(process_name))

        assert shell_name() == expected_shell_name


class TestRunCommand:
    @pytest.mark.parametrize(
        ("os_system", "shell", "command", "expected_full_command"),
        [
            ("Linux", "bash", "echo Hello, World!", "bash -c 'echo Hello, World!'"),
            ("Linux", "bash", "echo 'Hello, World!'", r"""bash -c 'echo '"'"'Hello, World!'"'"''"""),
            ("Linux", "zsh", "echo Hello, World!", "zsh -c 'echo Hello, World!'"),
            ("Linux", "sh", "echo Hello, World!", "sh -c 'echo Hello, World!'"),
            ("Linux", "ksh", "echo Hello, World!", "ksh -c 'echo Hello, World!'"),
            ("Linux", "fish", "echo Hello, World!", "fish -c 'echo Hello, World!'"),
            ("Linux", "dash", "echo Hello, World!", "dash -c 'echo Hello, World!'"),
            ("Linux", "ash", "echo Hello, World!", "ash -c 'echo Hello, World!'"),
            ("Linux", "csh", "echo Hello, World!", "csh -c 'echo Hello, World!'"),
            ("Windows", "powershell", "echo Hello, World!", r'''powershell.exe -Command "echo Hello, World!"'''),
            ("Windows", "cmd", "echo Hello, World!", 'cmd.exe /c "echo Hello, World!"'),
            ("Windows", "bash", "echo Hello, World!", "bash -c 'echo Hello, World!'"),
            ("Windows", "zsh", "echo Hello, World!", "zsh -c 'echo Hello, World!'"),
        ],
    )
    def test_run_command(self, mocker, os_system, shell, command, expected_full_command):
        mocker.patch("platform.system", return_value=os_system)
        mocker.patch(f"{C.PROJECT_MODULE}.util.shell_name", return_value=shell)
        mock = mocker.patch("subprocess.run")

        run_command(command)
        assert mock.called_with_once(expected_full_command, check=False)

    def test_run_command_suppress_called_process_error(self, mocker):
        mocker.patch("platform.system", return_value="Linux")
        mocker.patch(f"{C.PROJECT_MODULE}.util.shell_name", return_value="bash")
        mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "bash -c 'echo Hello, World!'"))

        try:
            run_command("echo 'Hello, World!'")
        except subprocess.CalledProcessError:
            pytest.fail("CalledProcessError should be suppressed")

    def test_run_command_unsupported_shell(self, mocker):
        # Mock platform.system
        mocker.patch("platform.system", return_value="Linux")
        mocker.patch(f"{C.PROJECT_MODULE}.util.shell_name", return_value="unsupported_shell")

        # Mock shell_name
        with pytest.raises(ValueError, match="Unsupported shell: unsupported_shell"):
            run_command("echo 'Hello, World!'")


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
