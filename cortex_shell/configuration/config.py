from __future__ import annotations

import os
from pathlib import Path

from pydantic import ValidationError

from .. import constants as C  # noqa: N812
from ..errors import InvalidConfigError
from ..role import DEFAULT_ROLE
from ..yaml import from_yaml_file, to_yaml_file
from .schema import (
    Configuration,
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
        path = Path.home() / ".config" / C.PROJECT_NAME
    return path.resolve()


class ConfigurationManager:
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
            self.config = from_yaml_file(Configuration, config_file).populate_roles()
        except ValidationError as e:
            raise InvalidConfigError(e) from None

    def config_directory(self) -> Path:
        return self._directory

    def config_file(self) -> Path:
        return self._directory / C.CONFIG_FILE

    def get_builtin_role_default(self) -> Role:
        return Role(
            name="default",
            description=DEFAULT_ROLE,
            options=self.config.default.options,
            output=self.config.default.output,
        )

    def get_role(self, role_id: str) -> Role | None:
        return next((role for role in self.config.roles if role.name == role_id), None)


_cfg = None


def cfg() -> ConfigurationManager:
    global _cfg  # noqa: PLW0603
    if _cfg is None:
        _cfg = ConfigurationManager()
    return _cfg


def set_cfg(config: ConfigurationManager) -> None:
    global _cfg  # noqa: PLW0603
    _cfg = config
