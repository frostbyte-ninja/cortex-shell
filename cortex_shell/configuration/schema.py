from pathlib import Path

import cfgv

from .. import constants as C  # noqa: N812
from ..types.cfgv import Array, Map
from ..util import get_temp_dir
from .validator import (
    check_api,
    check_color,
    check_float,
    check_greater_than_zero,
    check_path,
    check_role_name,
    check_str_optional,
    check_temperature,
    check_top_probability,
    check_url_optional,
)


class ConfigSchemaBuilder:
    @classmethod
    def build(cls) -> cfgv.Map:
        chat_gpt_dict = cls._build_chat_gpt_dict()
        apis_dict = cls._build_apis_dict(chat_gpt_dict)
        session_dict = cls._build_session_dict()
        misc_dict = cls._build_misc_dict(session_dict)
        options_dict = cls._build_options_dict()
        options_no_default_dict = cls._build_options_no_default_dict(options_dict)
        output_dict = cls._build_output_dict()
        output_dict_no_defaults = cls._build_output_dict_no_defaults(output_dict)
        default_dict = cls._build_default_dict(options_dict, output_dict)
        builtin_roles_dict = cls._build_builtin_roles_dict(options_no_default_dict)
        role_dict = cls._build_role_dict(options_no_default_dict, output_dict_no_defaults)

        return cfgv.Map(
            "configuration",
            None,
            cfgv.OptionalRecurse("apis", apis_dict, {}),
            cfgv.OptionalRecurse("misc", misc_dict, {}),
            cfgv.OptionalRecurse("default", default_dict, {}),
            cfgv.OptionalRecurse("builtin_roles", builtin_roles_dict, {}),
            cfgv.OptionalRecurse("roles", Array(role_dict), []),
            cfgv.NoAdditionalKeys(("apis", "misc", "default", "builtin_roles", "roles")),
        )

    @staticmethod
    def _build_chat_gpt_dict() -> cfgv.Map:
        return cfgv.Map(
            None,
            None,
            cfgv.Optional("api_key", check_str_optional, ""),
            cfgv.Optional("azure_endpoint", cfgv.check_and(check_str_optional, check_url_optional), ""),
            cfgv.Optional("azure_deployment", check_str_optional, ""),
        )

    @staticmethod
    def _build_apis_dict(chat_gpt_dict: cfgv.Map) -> cfgv.Map:
        return cfgv.Map(
            "apis",
            None,
            cfgv.OptionalRecurse("chatgpt", chat_gpt_dict, {}),
        )

    @staticmethod
    def _build_session_dict() -> cfgv.Map:
        return cfgv.Map(
            None,
            None,
            cfgv.Optional(
                "chat_history_path",
                check_path,
                (Path.home() / ".cache" / C.PROJECT_NAME / "history").resolve(),
            ),
            cfgv.Optional("chat_history_size", cfgv.check_and(cfgv.check_int, check_greater_than_zero), 100),
            cfgv.Optional("chat_cache_path", check_path, (get_temp_dir() / C.PROJECT_NAME / "cache").resolve()),
            cfgv.Optional("chat_cache_size", cfgv.check_and(cfgv.check_int, check_greater_than_zero), 100),
            cfgv.Optional("cache", cfgv.check_bool, True),
            cfgv.NoAdditionalKeys((
                "chat_history_path",
                "chat_history_size",
                "chat_cache_path",
                "chat_cache_size",
                "cache",
            )),
        )

    @staticmethod
    def _build_misc_dict(session_dict: cfgv.Map) -> cfgv.Map:
        return cfgv.Map(
            None,
            None,
            cfgv.Optional("request_timeout", cfgv.check_int, 10),
            cfgv.OptionalRecurse("session", session_dict, {}),
            cfgv.NoAdditionalKeys(("request_timeout", "session")),
        )

    @staticmethod
    def _build_options_dict() -> cfgv.Map:
        return cfgv.Map(
            None,
            None,
            cfgv.Optional("api", cfgv.check_and(cfgv.check_string, check_api), "chatgpt"),
            cfgv.Optional("model", cfgv.check_string, "gpt-4-1106-preview"),
            cfgv.Optional("temperature", cfgv.check_and(check_float, check_temperature), 0.1),
            cfgv.Optional("top_probability", cfgv.check_and(check_float, check_top_probability), 1.0),
            cfgv.NoAdditionalKeys(("api", "model", "temperature", "top_probability")),
        )

    @staticmethod
    def _build_options_no_default_dict(options_dict: cfgv.Map) -> Map:
        return Map(
            None,
            None,
            *(
                cfgv.OptionalNoDefault(item.key, item.check_fn)
                for item in options_dict.items
                if issubclass(type(item), cfgv.Optional)
            ),
            *(item for item in options_dict.items if not issubclass(type(item), cfgv.Optional)),
        )

    @staticmethod
    def _build_output_dict() -> cfgv.Map:
        return cfgv.Map(
            "output",
            None,
            cfgv.Optional("stream", cfgv.check_bool, True),
            cfgv.Optional("formatted", cfgv.check_bool, True),
            cfgv.Optional("color", cfgv.check_and(cfgv.check_string, check_color), "blue"),
            cfgv.Optional("theme", cfgv.check_string, "dracula"),
            cfgv.NoAdditionalKeys(("stream", "formatted", "color", "theme")),
        )

    @staticmethod
    def _build_output_dict_no_defaults(output_dict: cfgv.Map) -> Map:
        return Map(
            None,
            None,
            *(
                cfgv.OptionalNoDefault(item.key, item.check_fn)
                for item in output_dict.items
                if issubclass(type(item), cfgv.Optional)
            ),
            *(item for item in output_dict.items if not issubclass(type(item), cfgv.Optional)),
        )

    @staticmethod
    def _build_default_dict(options_dict: cfgv.Map, output_dict: cfgv.Map) -> cfgv.Map:
        return cfgv.Map(
            None,
            None,
            cfgv.OptionalNoDefault("role", cfgv.check_string),
            cfgv.OptionalRecurse("options", options_dict, {}),
            cfgv.OptionalRecurse("output", output_dict, {}),
            cfgv.NoAdditionalKeys(("role", "options", "output")),
        )

    @staticmethod
    def _build_builtin_roles_dict(options_no_default_dict: Map) -> cfgv.Map:
        return cfgv.Map(
            "builtin_roles",
            None,
            cfgv.OptionalRecurse(
                "code",
                cfgv.Map(
                    None,
                    None,
                    cfgv.OptionalRecurse("options", options_no_default_dict, {}),
                    cfgv.NoAdditionalKeys(("options",)),
                ),
                {},
            ),
            cfgv.OptionalRecurse(
                "shell",
                cfgv.Map(
                    None,
                    None,
                    cfgv.OptionalRecurse("options", options_no_default_dict, {}),
                    cfgv.Optional("default_execute", cfgv.check_bool, False),
                    cfgv.NoAdditionalKeys(("options", "default_execute")),
                ),
                {},
            ),
            cfgv.OptionalRecurse(
                "describe_shell",
                cfgv.Map(
                    None,
                    None,
                    cfgv.OptionalRecurse("options", options_no_default_dict, {}),
                    cfgv.NoAdditionalKeys(("options",)),
                ),
                {},
            ),
        )

    @staticmethod
    def _build_role_dict(options_no_default_dict: Map, output_dict_no_defaults: Map) -> cfgv.Map:
        return cfgv.Map(
            "role",
            None,
            cfgv.Required("name", cfgv.check_and(cfgv.check_string, check_role_name)),
            cfgv.Required("description", cfgv.check_string),
            cfgv.OptionalRecurse("options", options_no_default_dict, {}),
            cfgv.OptionalRecurse("output", output_dict_no_defaults, {}),
            cfgv.NoAdditionalKeys(("name", "description", "options", "output")),
        )
