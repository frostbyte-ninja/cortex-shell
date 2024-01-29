from __future__ import annotations

from pathlib import Path

import validators
from pathvalidate import validate_filepath

from cortex_shell.util import os_name, shell_name


def check_path(path: str) -> Path:
    if path:
        try:
            validate_filepath(path, platform="auto")
        except Exception as e:
            raise ValueError(f"{path!r} is not a valid path") from e
    return Path(path)


def check_api(api: str) -> str:
    supported_apis = {"chatgpt"}
    if api not in supported_apis:
        raise ValueError(f'"{api}" API is not supported. Valid options are "' + ", ".join(supported_apis))
    return api


def check_color(color: str) -> str:
    low_intensity = {"black", "red", "green", "yellow", "blue", "magenta", "cyan", "gray"}
    high_intensity = {
        "brightblack",
        "brightred",
        "brightgreen",
        "brightyellow",
        "brightblue",
        "brightmagenta",
        "brightcyan",
        "white",
    }
    all_colors = {*low_intensity, *high_intensity}
    if color not in all_colors:
        options = ", ".join(all_colors)
        raise ValueError(f'"{color}" is not a supported color. Valid options are: {options}')
    return color


def check_url(url: str) -> str:
    if not validators.url(url):
        raise ValueError(f'"{url}" is not a valid url')
    return url


def check_role_name(role_id: str) -> str:
    invalid_ids = ["default", "code", "shell", "describe_shell"]
    if role_id in invalid_ids:
        raise ValueError("id must be none of: " + ", ".join(invalid_ids))
    return role_id


def description_validator(description: str) -> str:
    return description.format(shell=shell_name(), os=os_name())
