from pathlib import Path

import pytest

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.configuration.config import Config, _get_default_directory, cfg
from cortex_shell.errors import InvalidConfigError
from cortex_shell.role import CODE_ROLE, DEFAULT_ROLE, DESCRIBE_SHELL_ROLE, SHELL_ROLE
from cortex_shell.util import get_temp_dir, os_name, shell_name


class TestConfig:
    def test_get_default_directory(self, monkeypatch):
        monkeypatch.setenv("CORTEX_SHELL_CONFIG_PATH", "/test/path")
        assert _get_default_directory() == Path("/test/path").resolve()
        monkeypatch.delenv("CORTEX_SHELL_CONFIG_PATH")

        monkeypatch.setenv("XDG_CACHE_HOME", "/test/xdg")
        assert _get_default_directory() == Path("/test/xdg/cortex-shell").resolve()
        monkeypatch.delenv("XDG_CACHE_HOME")

        assert _get_default_directory() == Path.home() / ".config" / "cortex-shell"

    def test_config_file(self):
        assert Config().config_file() == _get_default_directory() / C.CONFIG_FILE


class TestDefaultConfig:
    def test_chat_gpt_api_key(self):
        assert cfg().chat_gpt_api_key() is None

    def test_azure_endpoint(self):
        assert cfg().azure_endpoint() is None

    def test_azure_deployment(self):
        assert cfg().azure_deployment() is None

    def test_request_timeout(self):
        assert cfg().request_timeout() == 10

    def test_chat_history_path(self):
        assert cfg().chat_history_path() == (Path.home() / ".cache" / C.PROJECT_NAME / "history").resolve()

    def test_chat_history_size(self):
        assert cfg().chat_history_size() == 100

    def test_chat_cache_path(self):
        assert cfg().chat_cache_path() == (get_temp_dir() / C.PROJECT_NAME / "cache").resolve()

    def test_chat_cache_size(self):
        assert cfg().chat_cache_size() == 100

    def test_cache(self):
        assert cfg().cache()

    def test_default_role(self):
        assert cfg().default_role() is None

    def test_default_options(self):
        options = cfg().default_options()

        assert options.api == "chatgpt"
        assert options.model == "gpt-4-1106-preview"
        assert options.temperature == 0.1
        assert options.top_probability == 1.0

    def test_default_output(self):
        options = cfg().default_output()

        assert options.stream
        assert options.formatted
        assert options.color == "blue"
        assert options.theme == "dracula"

    def test_get_builtin_role_default(self):
        role = cfg().get_builtin_role_default()
        assert role.name == "default"
        assert role.description == DEFAULT_ROLE.format(shell=shell_name(), os=os_name())
        assert role.options == cfg().default_options()
        assert role.output == cfg().default_output()

    def test_get_builtin_role_code(self):
        role = cfg().get_builtin_role_code()
        assert role.name == "code"
        assert role.description == CODE_ROLE.format(shell=shell_name(), os=os_name())
        assert role.options == cfg().default_options()
        output = cfg().default_output()
        output.formatted = False
        assert role.output == output

    def test_get_builtin_role_shell(self):
        role = cfg().get_builtin_role_shell()
        assert role.name == "shell"
        assert role.description == SHELL_ROLE.format(shell=shell_name(), os=os_name())
        assert role.options == cfg().default_options()
        output = cfg().default_output()
        output.formatted = False
        assert role.output == output

    def test_get_builtin_role_describe_shell(self):
        role = cfg().get_builtin_role_describe_shell()
        assert role.name == "describe_shell"
        assert role.description == DESCRIBE_SHELL_ROLE.format(shell=shell_name(), os=os_name())
        assert role.options == cfg().default_options()
        assert role.output == cfg().default_output()

    def test_get_role(self):
        assert not cfg()._config.roles


class TestModifiedConfig:
    def test_chat_gpt_api_key(self, configuration_override):
        api_key = "12345678"
        changes = {("apis", "chatgpt", "api_key"): api_key}
        configuration_override(changes)
        assert cfg().chat_gpt_api_key() == api_key

    def test_azure_endpoint(self, configuration_override):
        endpoint = "https://example.com"
        changes = {("apis", "chatgpt", "azure_endpoint"): endpoint}
        configuration_override(changes)
        assert cfg().azure_endpoint() == endpoint

    def test_azure_deployment(self, configuration_override):
        deployment = "test_deployment"
        changes = {("apis", "chatgpt", "azure_deployment"): deployment}
        configuration_override(changes)
        assert cfg().azure_deployment() == deployment

    def test_request_timeout(self, configuration_override):
        timeout = 15
        changes = {("misc", "request_timeout"): timeout}
        configuration_override(changes)
        assert cfg().request_timeout() == timeout

    def test_chat_history_path(self, configuration_override):
        path = "/tmp/test_history_path"
        changes = {("misc", "session", "chat_history_path"): path}
        configuration_override(changes)
        assert cfg().chat_history_path() == Path(path)

    def test_chat_history_size(self, configuration_override):
        size = 200
        changes = {("misc", "session", "chat_history_size"): size}
        configuration_override(changes)
        assert cfg().chat_history_size() == size

    def test_chat_cache_path(self, configuration_override):
        path = "/tmp/test_cache_path"
        changes = {("misc", "session", "chat_cache_path"): path}
        configuration_override(changes)
        assert cfg().chat_cache_path() == Path(path)

    def test_chat_cache_size(self, configuration_override):
        size = 200
        changes = {("misc", "session", "chat_cache_size"): size}
        configuration_override(changes)
        assert cfg().chat_cache_size() == size

    def test_cache(self, configuration_override):
        cache = False
        changes = {("misc", "session", "cache"): cache}
        configuration_override(changes)
        assert cfg().cache() == cache

    def test_default_role(self, configuration_override):
        role = "test_role"
        changes = {("default", "role"): role}
        configuration_override(changes)
        assert cfg().default_role() == role

    def test_default_options(self, configuration_override):
        changes = {
            ("default", "options", "model"): "test_model",
            ("default", "options", "temperature"): 0.5,
            ("default", "options", "top_probability"): 0.9,
        }
        configuration_override(changes)
        options = cfg().default_options()
        assert options.model == "test_model"
        assert options.temperature == 0.5
        assert options.top_probability == 0.9

    def test_default_output(self, configuration_override):
        changes = {
            ("default", "output", "stream"): False,
            ("default", "output", "formatted"): False,
            ("default", "output", "color"): "red",
            ("default", "output", "theme"): "test_theme",
        }
        configuration_override(changes)
        output = cfg().default_output()
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
            {("misc", "session", "chat_history_size"): "123"},
            {("misc", "session", "chat_history_size"): -1},
            {("misc", "session", "chat_history_size"): 0},
            {("misc", "session", "chat_history_size"): "invalid_size"},
            {("misc", "session", "chat_cache_path"): 123},
            {("misc", "session", "chat_cache_size"): -1},
            {("misc", "session", "chat_cache_size"): 0},
            {("misc", "session", "chat_cache_size"): "123"},
            {("misc", "session", "chat_cache_size"): "invalid_size"},
            {("misc", "session", "cache"): "invalid_cache"},
            {("default", "role"): 123},
            {("default", "options", "api"): 123},
            {("default", "options", "model"): 123},
            {("default", "options", "temperature"): "invalid_temperature"},
            {("default", "options", "temperature"): "0.5"},
            {("default", "options", "top_probability"): "invalid_probability"},
            {("default", "options", "top_probability"): "0.5"},
            {("default", "output", "stream"): "invalid_stream"},
            {("default", "output", "formatted"): "invalid_formatted"},
            {("default", "output", "color"): 123},
            {("default", "output", "color"): "asdf"},
            {("default", "output", "theme"): 123},
            {("builtin_roles", "code", "options", "api"): 123},
            {("builtin_roles", "code", "options", "model"): 123},
            {("builtin_roles", "code", "options", "temperature"): "invalid_temperature"},
            {("builtin_roles", "code", "options", "temperature"): "0.5"},
            {("builtin_roles", "code", "options", "top_probability"): "invalid_probability"},
            {("builtin_roles", "code", "options", "top_probability"): "0.5"},
            {("builtin_roles", "shell", "options", "api"): 123},
            {("builtin_roles", "shell", "options", "model"): 123},
            {("builtin_roles", "shell", "options", "temperature"): "invalid_temperature"},
            {("builtin_roles", "shell", "options", "temperature"): "0.5"},
            {("builtin_roles", "shell", "options", "top_probability"): "invalid_probability"},
            {("builtin_roles", "shell", "options", "top_probability"): "0.5"},
            {("builtin_roles", "shell", "default_execute"): "invalid_execute"},
            {("builtin_roles", "describe_shell", "options", "api"): 123},
            {("builtin_roles", "describe_shell", "options", "model"): 123},
            {("builtin_roles", "describe_shell", "options", "temperature"): "invalid_temperature"},
            {("builtin_roles", "describe_shell", "options", "temperature"): "0.5"},
            {("builtin_roles", "describe_shell", "options", "top_probability"): "invalid_probability"},
            {("builtin_roles", "describe_shell", "options", "top_probability"): "0.5"},
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
    def test_invalid_config(self, configuration_override, changes):
        with pytest.raises(InvalidConfigError):
            configuration_override(changes)


class TestOverrideConfig:
    def test_default_role(self, configuration_override):
        role_name = "test_role"
        role_description = "Test role description"
        changes = {
            ("default", "role"): role_name,
            ("roles",): [{"name": role_name, "description": role_description}],
        }
        configuration_override(changes)
        assert cfg().default_role() == role_name
        role = cfg().get_role(role_name)
        assert role is not None
        assert role.name == role_name
        assert role.description == role_description

    def test_custom_role(self, configuration_override):
        custom_role_name = "test_role"
        custom_role_description = "Test role description"

        changes = {
            ("default", "options", "model"): "test123",
            ("default", "options", "temperature"): 0.5,
            ("default", "options", "top_probability"): 0.7,
            ("default", "output", "color"): "green",
            ("default", "output", "theme"): "abcd",
            ("roles",): [{"name": custom_role_name, "description": custom_role_description}],
        }
        configuration_override(changes)
        role = cfg().get_role(custom_role_name)

        assert role.options.model == "test123"
        assert role.options.temperature == 0.5
        assert role.options.top_probability == 0.7
        assert role.output.color == "green"
        assert role.output.theme == "abcd"

    def test_missing_custom_role(self, configuration_override):
        changes = {
            ("roles",): [{"name": "some_role", "description": "description"}],
        }
        configuration_override(changes)
        assert cfg().get_role("tes1t_role") is None

    def test_builtin_roles(self, configuration_override):
        changes = {
            ("default", "options", "model"): "test123",
            ("default", "options", "temperature"): 0.5,
            ("default", "options", "top_probability"): 0.7,
        }
        configuration_override(changes)

        for role in (
            cfg().get_builtin_role_code(),
            cfg().get_builtin_role_shell(),
            cfg().get_builtin_role_describe_shell(),
        ):
            assert role.options.model == "test123"
            assert role.options.temperature == 0.5
            assert role.options.top_probability == 0.7
