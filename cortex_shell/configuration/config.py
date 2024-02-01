from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, cast

from pydantic import ValidationError

from .. import constants as C  # noqa: N812
from ..errors import InvalidConfigError
from ..role import DEFAULT_ROLE
from ..yaml import from_yaml_file, to_yaml_file
from .schema import (
    BuiltinRoleCode,
    BuiltinRoleDescribeShell,
    BuiltinRoleShell,
    Configuration,
    Options,
    Output,
    Role,
)


def _get_default_directory() -> Path:
    """Returns the default directory for the Configuration. This is intentionally
    underscored to indicate that `Configuration.get_default_directory` is the intended
    way to get this information. This is also done so `Configuration.get_default_directory`
    can be mocked in tests and `_get_default_directory` can be tested.
    """
    if path_str := os.environ.get("CORTEX_SHELL_CONFIG_PATH"):
        path = Path(path_str)
    else:
        path = Path(os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".config")) / C.PROJECT_NAME
    return path.resolve()


class Config:
    def __init__(self, directory: Path | None = None) -> None:
        self._init_config_directory(directory or _get_default_directory())
        self._load_config()

    def _init_config_directory(self, directory: Path) -> None:
        self._directory = directory
        self._directory.mkdir(exist_ok=True, parents=True)

    def _load_config(self) -> None:
        config_file = self.config_file()

        if not config_file.exists():
            to_yaml_file(config_file, Configuration())

        try:
            self._config = from_yaml_file(Configuration, config_file)

            # Fill empty values in roles with values from the default section
            for role in list(self._config.builtin_roles.__dict__.values()) + (self._config.roles or []):
                role.fill_from(self.get_builtin_role_default())
        except ValidationError as e:
            raise InvalidConfigError(e) from None

    def config_file(self) -> Path:
        return self._directory / C.CONFIG_FILE

    def chat_gpt_api_key(self) -> str | None:
        return cast(Optional[str], self._get_nested_value("apis", "chatgpt", "api_key"))

    def azure_endpoint(self) -> str | None:
        return cast(Optional[str], self._get_nested_value("apis", "chatgpt", "azure_endpoint"))

    def azure_deployment(self) -> str | None:
        return cast(Optional[str], self._get_nested_value("apis", "chatgpt", "azure_deployment"))

    def request_timeout(self) -> int:
        return cast(int, self._get_nested_value("misc", "request_timeout"))

    def chat_history_path(self) -> Path:
        return Path(self._get_nested_value("misc", "session", "chat_history_path"))

    def chat_history_size(self) -> int:
        return cast(int, self._get_nested_value("misc", "session", "chat_history_size"))

    def chat_cache_path(self) -> Path:
        return Path(self._get_nested_value("misc", "session", "chat_cache_path"))

    def chat_cache_size(self) -> int:
        return cast(int, self._get_nested_value("misc", "session", "chat_cache_size"))

    def cache(self) -> bool:
        return cast(bool, self._get_nested_value("misc", "session", "cache"))

    def default_role(self) -> str | None:
        value = self._get_nested_value("default", "role")
        return cast(str, value) if value else None

    def default_options(self) -> Options:
        return cast(Options, self._get_nested_value("default", "options"))

    def default_output(self) -> Output:
        return cast(Output, self._get_nested_value("default", "output"))

    def get_builtin_role_default(self) -> Role:
        return Role(
            name="default",
            description=DEFAULT_ROLE,
            options=self.default_options(),
            output=self.default_output(),
        )

    def get_builtin_role_code(self) -> BuiltinRoleCode:
        return cast(
            BuiltinRoleCode,
            self._get_nested_value("builtin_roles", "code"),
        )

    def get_builtin_role_shell(self) -> BuiltinRoleShell:
        return cast(
            BuiltinRoleShell,
            self._get_nested_value("builtin_roles", "shell"),
        )

    def get_builtin_role_describe_shell(self) -> BuiltinRoleDescribeShell:
        return cast(
            BuiltinRoleDescribeShell,
            self._get_nested_value("builtin_roles", "describe_shell"),
        )

    def get_role(self, role_id: str) -> Role | None:
        roles = self._get_nested_value("roles")
        if not roles:
            return None

        return next((role for role in roles if role.name == role_id), None)

    def _get_nested_value(self, *keys: str) -> Any:
        current_value: Any = self._config
        for key in keys:
            if isinstance(current_value, dict):
                current_value = current_value.get(key)
            else:
                current_value = getattr(current_value, key, None)
            if current_value is None:
                break
        return current_value


_cfg = None


def cfg() -> Config:
    global _cfg  # noqa: PLW0603
    if _cfg is None:
        _cfg = Config()
    return _cfg


def set_cfg(config: Config) -> None:
    global _cfg  # noqa: PLW0603
    _cfg = config
