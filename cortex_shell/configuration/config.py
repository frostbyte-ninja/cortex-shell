from __future__ import annotations

import functools
import os
from pathlib import Path
from typing import Any, Optional, cast

import cfgv

from .. import constants as C  # noqa: N812
from ..errors import InvalidConfigError
from ..role import CODE_ROLE, DEFAULT_ROLE, DESCRIBE_SHELL_ROLE, SHELL_ROLE, Options, Output, Role, ShellRole
from ..yaml import get_default_from_schema, yaml_dump, yaml_load
from .schema import CONFIG_SCHEMA


def _get_default_directory() -> Path:
    """Returns the default directory for the Configuration. This is intentionally
    underscored to indicate that `Configuration.get_default_directory` is the intended
    way to get this information. This is also done so `Configuration.get_default_directory`
    can be mocked in tests and `_get_default_directory` can be tested.
    """
    if path_str := os.environ.get("CORTEX_SHELL_CONFIG_PATH"):
        path = Path(path_str)
    else:
        path = Path(os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".config").resolve()) / C.PROJECT_NAME
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
            # new config file with default values
            self._config = get_default_from_schema(CONFIG_SCHEMA)
            yaml_dump(self._config, config_file.open("w"))
        else:
            # existing config file with added default values
            self._config = cfgv.load_from_filename(
                filename=config_file,
                schema=CONFIG_SCHEMA,
                load_strategy=functools.partial(yaml_load),
                exc_tp=InvalidConfigError,
            )

    def config_file(self) -> Path:
        return self._directory / C.CONFIG_FILE

    def chat_gpt_api_key(self) -> str | None:
        return cast(Optional[str], self._get_nested_value(["apis", "chatgpt", "api_key"]))

    def azure_endpoint(self) -> str | None:
        return cast(Optional[str], self._get_nested_value(["apis", "chatgpt", "azure_endpoint"]))

    def azure_deployment(self) -> str | None:
        return cast(Optional[str], self._get_nested_value(["apis", "chatgpt", "azure_deployment"]))

    def request_timeout(self) -> int:
        return cast(int, self._get_nested_value(["misc", "request_timeout"]))

    def chat_history_path(self) -> Path:
        return Path(self._get_nested_value(["misc", "session", "chat_history_path"]))

    def chat_history_size(self) -> int:
        return cast(int, self._get_nested_value(["misc", "session", "chat_history_size"]))

    def chat_cache_path(self) -> Path:
        return Path(self._get_nested_value(["misc", "session", "chat_cache_path"]))

    def chat_cache_size(self) -> int:
        return cast(int, self._get_nested_value(["misc", "session", "chat_cache_size"]))

    def cache(self) -> bool:
        return cast(bool, self._get_nested_value(["misc", "session", "cache"]))

    def default_role(self) -> str | None:
        value = self._get_nested_value(["default", "role"])
        return cast(str, value) if value else None

    def default_options(self) -> Options:
        return Options(**self._get_nested_value(["default", "options"]))

    def default_output(self) -> Output:
        return Output(**self._get_nested_value(["default", "output"]))

    def get_builtin_role_default(self) -> Role:
        return Role("default", DEFAULT_ROLE, self.default_options(), self.default_output())

    def get_builtin_role_code(self) -> Role:
        if val := self._get_nested_value(["builtin_roles", "code", "options"]):
            options = Options.from_dict(val)
        else:
            options = self.default_options()
        output = self.default_output()
        output.formatted = False
        return Role("code", CODE_ROLE, options, output)

    def get_builtin_role_shell(self) -> ShellRole:
        if val := self._get_nested_value(["builtin_roles", "shell", "options"]):
            options = Options.from_dict(val)
        else:
            options = self.default_options()
        output = self.default_output()
        output.formatted = False
        default_execute = self._get_nested_value(["builtin_roles", "shell", "default_execute"])
        return ShellRole("shell", SHELL_ROLE, default_execute, options, output)

    def get_builtin_role_describe_shell(self) -> Role:
        if val := self._get_nested_value(["builtin_roles", "describe_shell", "options"]):
            options = Options.from_dict(val)
        else:
            options = self.default_options()
        output = self.default_output()
        return Role("describe_shell", DESCRIBE_SHELL_ROLE, options, output)

    def get_role(self, role_id: str) -> Role | None:
        if self._config["roles"]:
            role_data = next((entry for entry in self._config["roles"] if entry["name"] == role_id), None)
            if role_data:
                options = Options.from_dict(role_data.get("options"))
                output = Output.from_dict(role_data.get("output"))
                role = Role(role_data["name"], role_data["description"], options, output)
                role.fill_from(self.get_builtin_role_default())
                return role
        return None

    def _get_nested_value(self, keys: list[str], default: Any = None) -> Any:
        return functools.reduce(
            lambda d, key: d.get(key, default) if isinstance(d, dict) else default,
            keys,
            self._config,
        )


_cfg = None


def cfg() -> Config:
    global _cfg  # noqa: PLW0603
    if _cfg is None:
        _cfg = Config()
    return _cfg


def set_cfg(config: Config) -> None:
    global _cfg  # noqa: PLW0603
    _cfg = config
