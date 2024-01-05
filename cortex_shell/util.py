from __future__ import annotations

import contextlib
import errno
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
from importlib import resources
from pathlib import Path
from tempfile import gettempdir
from typing import Any, Callable

import distro
import psutil
import typer
from prompt_toolkit.formatted_text import FormattedText

from . import constants as C  # noqa: N812


def option_callback(func: Callable[[Any, str], Any]) -> Callable[[Any, str], Any]:
    def wrapper(cls: Any, value: str) -> None:
        if not value:
            return
        func(cls, value)
        raise typer.Exit

    return wrapper


def get_resource_file(resource_name: str, submodule: str = "") -> Path:
    module = f"{C.PROJECT_MODULE}.resources"
    if submodule:
        module = f"{module}.{submodule}"
    with resources.as_file(resources.files(module) / resource_name) as path:
        return path


@option_callback
def print_version_callback(*_args: Any) -> None:
    typer.echo(f"v{C.VERSION}")


@option_callback
def install_shell_integration(*_args: Any) -> None:
    """
    Installs shell integration.
    Allows user to get shell completions in terminal by using hotkey.
    Allows user to edit shell command right away in terminal.
    """

    shell = shell_name()
    if shell == "bash":
        shell_config_path = Path.home() / ".bashrc"
    elif shell == "zsh":
        shell_config_path = Path.home() / ".zshrc"
    elif shell == "fish":
        shell_config_path = Path.home() / ".config" / "fish" / "config.fish"
        shell_config_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        typer.echo(f'Your shell "{shell}" is not supported.')
        return

    marker = "# cortex-shell integration"
    with get_resource_file(shell, "shell_integrations").open("r", encoding="utf-8") as source:
        new_content = f"{marker}\n{source.read().strip()}\n{marker}"

    if shell_config_path.is_file():
        with shell_config_path.open("r", encoding="utf-8", newline="\n") as target:
            original_content = target.read()

        if marker in original_content:
            content_parts = original_content.split(marker)
            updated_content = f"{content_parts[0]}{new_content}{content_parts[2]}"
        else:
            updated_content = f"{original_content}\n{new_content}\n"
    else:
        updated_content = new_content + "\n"

    with shell_config_path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(updated_content)

    typer.echo(f'Integration for "{shell}" shell successfully installed. Restart your terminal to apply changes.')


def get_colored_text(text: str, color: str) -> FormattedText:
    color = "".join(c for c in color if c.islower())
    return FormattedText([(f"ansi{color} bold", text)])


def os_name() -> str:
    current_platform = platform.system()
    if current_platform == "Linux":
        current_platform = "Linux/" + distro.name(pretty=True)
    if current_platform == "Windows":
        current_platform = "Windows " + platform.release()
    if current_platform == "Darwin":
        current_platform = "Darwin/MacOS " + platform.mac_ver()[0]
    return current_platform


def shell_name() -> str | None:
    def name_transform(process_path: str) -> str:
        process_name = Path(process_path).stem
        is_powershell = re.fullmatch("pwsh|pwsh.exe|powershell.exe", process_name)
        return "powershell" if is_powershell else process_name

    try:
        process = psutil.Process(os.getppid())
        while any(name in process.name().lower() for name in ("python", C.PROJECT_NAME, C.PROJECT_NAME_SHORT)):
            process = process.parent()

        return name_transform(process.name())

    except Exception:
        return None


def run_command(command: str) -> None:
    """
    Runs a command in the user's shell.
    It is aware of the current user's $SHELL.
    :param command: A shell command to run.
    """
    shell = shell_name()

    if shell == "powershell":
        full_command = ["powershell.exe", "-Command", f'"{command}"']
    elif shell == "cmd":
        full_command = ["cmd.exe", "/c", f'"{command}"']
    elif shell in {"bash", "zsh", "sh", "ksh", "fish", "dash", "ash", "csh", "tcsh"}:
        full_command = [shell, "-c", command]
    else:
        raise ValueError(f"Unsupported shell: {shell}")

    with contextlib.suppress(subprocess.CalledProcessError):
        subprocess.run(full_command, check=False)


def has_stdin() -> bool:
    return not sys.stdin.isatty()


def get_stdin() -> str:
    return sys.stdin.read()


def is_tty() -> bool:
    return sys.stdout.isatty()


def get_temp_dir() -> Path:
    return Path(gettempdir())


def rmtree(path: Path) -> None:
    def handle_remove_readonly(
        func: Callable[..., Any],
        path_str: str,
        exc: Exception,
    ) -> None:
        if (
            func in {os.rmdir, os.remove, os.unlink}
            and isinstance(exc, OSError)
            and exc.errno in {errno.EACCES, errno.EPERM}
        ):
            path_ = Path(path_str)
            for p in (path_, path_.parent):
                p.chmod(p.stat().st_mode | stat.S_IWUSR)
            func(path_)
        else:
            raise exc

    if path.exists():
        if sys.version_info >= (3, 12):
            shutil.rmtree(path, ignore_errors=False, onexc=handle_remove_readonly)
        else:
            # remove this when Python 3.12 becomes the oldest supported release
            shutil.rmtree(path, onerror=lambda func, path_str, exc: handle_remove_readonly(func, path_str, exc[1]))
