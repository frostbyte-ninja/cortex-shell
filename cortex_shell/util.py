from __future__ import annotations

import contextlib
import errno
import os
import platform
import shutil
import stat
import subprocess
import sys
from collections.abc import Container
from copy import deepcopy
from importlib import resources
from pathlib import Path
from tempfile import gettempdir
from typing import Any, Callable, cast

import click.exceptions
import distro
import typer
from pathvalidate import is_valid_filepath
from prompt_toolkit import print_formatted_text as print_formatted_text_orig
from prompt_toolkit.formatted_text import FormattedText
from pydantic import BaseModel
from shellingham import ShellDetectionFailure, detect_shell

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


def get_powershell_profile_path(shell: str) -> Path | None:
    if shell not in {"powershell", "pwsh"}:
        raise ValueError(f'"{shell}" shell is not supported.')

    command = f'{shell} -NoProfile -Command "$PROFILE"'
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    path = result.stdout.strip()

    if result.returncode != 0 or not is_valid_filepath(path, platform="auto"):
        return None

    return Path(path)


@option_callback
def install_shell_integration(*_args: Any) -> None:
    """
    Installs shell integration.
    Allows user to get shell completions in terminal by using hotkey.
    Allows user to edit shell command right away in terminal.
    """

    shell = shell_name()
    shell_config_path: Path | None

    if shell == "bash":
        shell_config_path = Path.home() / ".bashrc"
    elif shell == "zsh":
        shell_config_path = Path.home() / ".zshrc"
    elif shell == "fish":
        shell_config_path = Path.home() / ".config" / "fish" / "config.fish"
        shell_config_path.parent.mkdir(parents=True, exist_ok=True)
    elif shell == "powershell":
        shell_config_path = get_powershell_profile_path("powershell")
    elif shell == "pwsh":
        shell_config_path = get_powershell_profile_path("pwsh")
    else:
        typer.echo(f'"{shell}" shell is not supported.')
        return

    if not shell_config_path:
        raise click.ClickException(f'Could not determine "{shell}" config file')

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

    shell_config_path.parent.mkdir(parents=True, exist_ok=True)
    with shell_config_path.open("w", encoding="utf-8", newline="\n") as target:
        target.write(updated_content)

    typer.echo(f'Integration for "{shell}" successfully installed. Restart your terminal to apply changes.')


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
    try:
        return cast(str, detect_shell()[0])
    except ShellDetectionFailure:
        return None


def run_command(command: str) -> None:
    """
    Runs a command in the user's shell.
    It is aware of the current user's $SHELL.
    :param command: A shell command to run.
    """
    shell = shell_name()

    if shell is None:
        raise ValueError("Unsupported shell")
    if shell == "powershell":
        full_command = ["powershell", "-Command", f'"{command}"']
    elif shell == "pwsh":
        full_command = ["pwsh", "-Command", f'"{command}"']
    elif shell == "cmd":
        full_command = ["cmd", "/c", f'"{command}"']
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
    temp_dir = Path(gettempdir()) / C.PROJECT_NAME
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def get_cache_dir() -> Path:
    cache_dir = Path.home() / ".cache" / C.PROJECT_NAME
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def print_formatted_text(*values: str | FormattedText, **kwargs: Any) -> None:
    # workaround for NoConsoleScreenBufferError
    if is_tty():
        print_formatted_text_orig(*values, **kwargs)
    else:

        def to_text(val: Any) -> str:
            if isinstance(val, str):
                return val
            elif isinstance(val, list):
                return "".join([v[1] for v in val])
            else:
                raise TypeError

        end = kwargs.get("end", "\n")
        sep = kwargs.get("sep", " ")
        print(sep.join([to_text(value) for value in values]), end=end)


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


def fill_values(source: BaseModel, target: BaseModel) -> None:
    for attr, value in vars(source).items():
        target_value = getattr(target, attr, None)

        if target_value is None:
            setattr(target, attr, deepcopy(value))
        elif isinstance(value, Container) and not target_value:
            continue
        elif isinstance(value, BaseModel) and isinstance(target_value, BaseModel):
            fill_values(value, target_value)
