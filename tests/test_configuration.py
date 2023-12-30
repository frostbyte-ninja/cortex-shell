from pathlib import Path

import pytest

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.configuration.config import Config, _get_default_directory
from cortex_shell.configuration.schema import CONFIG_SCHEMA
from cortex_shell.errors import InvalidConfigError
from cortex_shell.role import CODE_ROLE, DEFAULT_ROLE, DESCRIBE_SHELL_ROLE, SHELL_ROLE
from cortex_shell.util import get_temp_dir, os_name, shell_name
from cortex_shell.yaml import get_default_from_schema, yaml_dump


@pytest.fixture()
def mock_default_config(tmp_dir_factory):
    config_dir = tmp_dir_factory.get()
    config_file = config_dir / C.CONFIG_FILE
    yaml_dump(get_default_from_schema(CONFIG_SCHEMA), config_file.open("w"))
    return Config(directory=config_dir)


@pytest.fixture()
def modified_config_factory(tmp_dir_factory):
    def _modified_config_factory(changes):
        config_dir = tmp_dir_factory.get()
        config_file = config_dir / C.CONFIG_FILE
        modified_config_data = get_default_from_schema(CONFIG_SCHEMA)

        # Apply changes to the config data
        for key_path, value in changes.items():
            config_entry = modified_config_data
            for key in key_path[:-1]:
                config_entry = config_entry[key]
            config_entry[key_path[-1]] = value

        yaml_dump(modified_config_data, config_file.open("w"))
        return Config(directory=config_dir)

    return _modified_config_factory


class TestConfig:
    def test_get_default_directory(self, monkeypatch):
        monkeypatch.setenv("CORTEX_SHELL_CONFIG_PATH", "/test/path")
        assert _get_default_directory() == Path("/test/path").resolve()
        monkeypatch.delenv("CORTEX_SHELL_CONFIG_PATH")

        monkeypatch.setenv("XDG_CACHE_HOME", "/test/xdg")
        assert _get_default_directory() == Path("/test/xdg/cortex_shell").resolve()
        monkeypatch.delenv("XDG_CACHE_HOME")

        assert _get_default_directory() == Path.home() / ".config" / "cortex_shell"

    def test_config_file(self):
        assert Config().config_file() == _get_default_directory() / C.CONFIG_FILE


class TestDefaultConfig:
    def test_chat_gpt_api_key(self, mock_default_config):
        assert mock_default_config.chat_gpt_api_key() is None

    def test_azure_endpoint(self, mock_default_config):
        assert mock_default_config.azure_endpoint() is None

    def test_azure_deployment(self, mock_default_config):
        assert mock_default_config.azure_deployment() is None

    def test_request_timeout(self, mock_default_config):
        assert mock_default_config.request_timeout() == 10

    def test_chat_history_path(self, mock_default_config):
        assert mock_default_config.chat_history_path() == get_temp_dir() / C.PROJECT_MODULE / "history"

    def test_chat_history_size(self, mock_default_config):
        assert mock_default_config.chat_history_size() == 100

    def test_chat_cache_path(self, mock_default_config):
        assert mock_default_config.chat_cache_path() == get_temp_dir() / C.PROJECT_MODULE / "cache"

    def test_chat_cache_size(self, mock_default_config):
        assert mock_default_config.chat_cache_size() == 100

    def test_cache(self, mock_default_config):
        assert mock_default_config.cache()

    def test_default_role(self, mock_default_config):
        assert mock_default_config.default_role() is None

    def test_default_options(self, mock_default_config):
        options = mock_default_config.default_options()

        assert options.api == "chatgpt"
        assert options.model == "gpt-4-1106-preview"
        assert options.temperature == 0.1
        assert options.top_probability == 1.0

    def test_default_output(self, mock_default_config):
        options = mock_default_config.default_output()

        assert options.stream
        assert options.formatted
        assert options.color == "blue"
        assert options.theme == "dracula"

    def test_get_builtin_role_default(self, mock_default_config):
        role = mock_default_config.get_builtin_role_default()
        assert role.name == "default"
        assert role.description == DEFAULT_ROLE.format(shell=shell_name(), os=os_name())
        assert role.options == mock_default_config.default_options()
        assert role.output == mock_default_config.default_output()

    def test_get_builtin_role_code(self, mock_default_config):
        role = mock_default_config.get_builtin_role_code()
        assert role.name == "code"
        assert role.description == CODE_ROLE.format(shell=shell_name(), os=os_name())
        assert role.options == mock_default_config.default_options()
        output = mock_default_config.default_output()
        output.formatted = False
        assert role.output == output

    def test_get_builtin_role_shell(self, mock_default_config):
        role = mock_default_config.get_builtin_role_shell()
        assert role.name == "shell"
        assert role.description == SHELL_ROLE.format(shell=shell_name(), os=os_name())
        assert role.options == mock_default_config.default_options()
        output = mock_default_config.default_output()
        output.formatted = False
        assert role.output == output

    def test_get_builtin_role_describe_shell(self, mock_default_config):
        role = mock_default_config.get_builtin_role_describe_shell()
        assert role.name == "describe_shell"
        assert role.description == DESCRIBE_SHELL_ROLE.format(shell=shell_name(), os=os_name())
        assert role.options == mock_default_config.default_options()
        assert role.output == mock_default_config.default_output()

    def test_get_role(self, mock_default_config):
        assert mock_default_config._config["roles"] == []


class TestModifiedConfig:
    def test_chat_gpt_api_key(self, modified_config_factory):
        api_key = "12345678"
        changes = {("apis", "chatgpt", "api_key"): api_key}
        config = modified_config_factory(changes)
        assert config.chat_gpt_api_key() == api_key

    def test_azure_endpoint(self, modified_config_factory):
        endpoint = "https://example.com"
        changes = {("apis", "chatgpt", "azure_endpoint"): endpoint}
        config = modified_config_factory(changes)
        assert config.azure_endpoint() == endpoint

    def test_azure_deployment(self, modified_config_factory):
        deployment = "test_deployment"
        changes = {("apis", "chatgpt", "azure_deployment"): deployment}
        config = modified_config_factory(changes)
        assert config.azure_deployment() == deployment

    def test_request_timeout(self, modified_config_factory):
        timeout = 15
        changes = {("misc", "request_timeout"): timeout}
        config = modified_config_factory(changes)
        assert config.request_timeout() == timeout

    def test_chat_history_path(self, modified_config_factory):
        path = "/tmp/test_history_path"
        changes = {("misc", "session", "chat_history_path"): path}
        config = modified_config_factory(changes)
        assert config.chat_history_path() == Path(path)

    def test_chat_history_size(self, modified_config_factory):
        size = 200
        changes = {("misc", "session", "chat_history_size"): size}
        config = modified_config_factory(changes)
        assert config.chat_history_size() == size

    def test_chat_cache_path(self, modified_config_factory):
        path = "/tmp/test_cache_path"
        changes = {("misc", "session", "chat_cache_path"): path}
        config = modified_config_factory(changes)
        assert config.chat_cache_path() == Path(path)

    def test_chat_cache_size(self, modified_config_factory):
        size = 200
        changes = {("misc", "session", "chat_cache_size"): size}
        config = modified_config_factory(changes)
        assert config.chat_cache_size() == size

    def test_cache(self, modified_config_factory):
        cache = False
        changes = {("misc", "session", "cache"): cache}
        config = modified_config_factory(changes)
        assert config.cache() == cache

    def test_default_role(self, modified_config_factory):
        role = "test_role"
        changes = {("default", "role"): role}
        config = modified_config_factory(changes)
        assert config.default_role() == role

    def test_default_options(self, modified_config_factory):
        changes = {
            ("default", "options", "model"): "test_model",
            ("default", "options", "temperature"): 0.5,
            ("default", "options", "top_probability"): 0.9,
        }
        config = modified_config_factory(changes)
        options = config.default_options()
        assert options.model == "test_model"
        assert options.temperature == 0.5
        assert options.top_probability == 0.9

    def test_default_output(self, modified_config_factory):
        changes = {
            ("default", "output", "stream"): False,
            ("default", "output", "formatted"): False,
            ("default", "output", "color"): "red",
            ("default", "output", "theme"): "test_theme",
        }
        config = modified_config_factory(changes)
        output = config.default_output()
        assert output.stream is False
        assert output.formatted is False
        assert output.color == "red"
        assert output.theme == "test_theme"


class TestInvalidConfig:
    @pytest.mark.parametrize(
        "changes",
        [
            {("apis", "chatgpt", "api_key"): 123},
            {("apis", "chatgpt", "azure_endpoint"): 123},
            {("apis", "chatgpt", "azure_deployment"): 123},
            {("misc", "request_timeout"): "invalid_timeout"},
            {("misc", "session", "chat_history_path"): 123},
            {("misc", "session", "chat_history_size"): "invalid_size"},
            {("misc", "session", "chat_cache_path"): 123},
            {("misc", "session", "chat_cache_size"): "invalid_size"},
            {("misc", "session", "cache"): "invalid_cache"},
            {("default", "options", "default_role"): 123},
            {("default", "options", "api"): 123},
            {("default", "options", "model"): 123},
            {("default", "options", "temperature"): "invalid_temperature"},
            {("default", "options", "top_probability"): "invalid_probability"},
            {("default", "output", "stream"): "invalid_stream"},
            {("default", "output", "formatted"): "invalid_formatted"},
            {("default", "output", "color"): 123},
            {("default", "output", "theme"): 123},
            {("builtin_roles", "code", "options", "api"): 123},
            {("builtin_roles", "code", "options", "model"): 123},
            {("builtin_roles", "code", "options", "temperature"): "invalid_temperature"},
            {("builtin_roles", "code", "options", "top_probability"): "invalid_probability"},
            {("builtin_roles", "shell", "options", "api"): 123},
            {("builtin_roles", "shell", "options", "model"): 123},
            {("builtin_roles", "shell", "options", "temperature"): "invalid_temperature"},
            {("builtin_roles", "shell", "options", "top_probability"): "invalid_probability"},
            {("builtin_roles", "shell", "default_execute"): "invalid_execute"},
            {("builtin_roles", "describe_shell", "options", "api"): 123},
            {("builtin_roles", "describe_shell", "options", "model"): 123},
            {("builtin_roles", "describe_shell", "options", "temperature"): "invalid_temperature"},
            {("builtin_roles", "describe_shell", "options", "top_probability"): "invalid_probability"},
            {("roles",): [{"name": 123, "description": "Test role"}]},
            {("roles",): [{"name": "test_role", "description": 123}]},
            {("roles",): [{"name": "test_role", "description": "Test role", "options": {"api": 123}}]},
            {("roles",): [{"name": "test_role", "description": "Test role", "options": {"model": 123}}]},
            {
                ("roles",): [
                    {
                        "name": "test_role",
                        "description": "Test role",
                        "options": {"temperature": "invalid_temperature"},
                    },
                ],
            },
            {
                ("roles",): [
                    {
                        "name": "test_role",
                        "description": "Test role",
                        "options": {"top_probability": "invalid_probability"},
                    },
                ],
            },
            {("roles",): [{"name": "test_role", "description": "Test role", "output": {"stream": "invalid_stream"}}]},
            {
                ("roles",): [
                    {"name": "test_role", "description": "Test role", "output": {"formatted": "invalid_formatted"}},
                ],
            },
            {("roles",): [{"name": "test_role", "description": "Test role", "output": {"color": 123}}]},
            {("roles",): [{"name": "test_role", "description": "Test role", "output": {"theme": 123}}]},
        ],
    )
    def test_invalid_config(self, modified_config_factory, changes):
        with pytest.raises(InvalidConfigError):
            modified_config_factory(changes)


class TestOverrideConfig:
    def test_default_role(self, modified_config_factory):
        role_name = "test_role"
        role_description = "Test role description"
        changes = {
            ("default", "role"): role_name,
            ("roles",): [{"name": role_name, "description": role_description}],
        }
        config = modified_config_factory(changes)
        assert config.default_role() == role_name
        role = config.get_role(role_name)
        assert role is not None
        assert role.name == role_name
        assert role.description == role_description
