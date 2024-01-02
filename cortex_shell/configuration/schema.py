import cfgv

from .. import constants as C  # noqa: N812
from ..types.cfgv import Array, Map
from ..util import get_temp_dir
from .validators import (
    check_api,
    check_color,
    check_float,
    check_path,
    check_role_name,
    check_str_optional,
    check_temperature,
    check_top_probability,
    check_url,
)

CHAT_GPT_DICT = cfgv.Map(
    None,
    None,
    cfgv.Optional("api_key", check_str_optional, ""),
    cfgv.Optional("azure_endpoint", cfgv.check_and(check_str_optional, check_url), ""),
    cfgv.Optional("azure_deployment", check_str_optional, ""),
)

APIS_DICT = cfgv.Map(
    "apis",
    None,
    cfgv.OptionalRecurse(
        "chatgpt",
        CHAT_GPT_DICT,
        {},
    ),
)

SESSION_DICT = cfgv.Map(
    None,
    None,
    cfgv.Optional("chat_history_path", check_path, get_temp_dir() / C.PROJECT_NAME / "history"),
    cfgv.Optional("chat_history_size", cfgv.check_int, 100),
    cfgv.Optional("chat_cache_path", check_path, get_temp_dir() / C.PROJECT_NAME / "cache"),
    cfgv.Optional("chat_cache_size", cfgv.check_int, 100),
    cfgv.Optional("cache", cfgv.check_bool, True),
    cfgv.NoAdditionalKeys(("chat_history_path", "chat_history_size", "chat_cache_path", "chat_cache_size", "cache")),
)

MISC_DICT = cfgv.Map(
    None,
    None,
    cfgv.Optional("request_timeout", cfgv.check_int, 10),
    cfgv.OptionalRecurse("session", SESSION_DICT, {}),
    cfgv.NoAdditionalKeys(("request_timeout", "session")),
)

OPTIONS_DICT = cfgv.Map(
    None,
    None,
    cfgv.Optional("api", cfgv.check_and(cfgv.check_string, check_api), "chatgpt"),
    cfgv.Optional("model", cfgv.check_string, "gpt-4-1106-preview"),
    cfgv.Optional("temperature", cfgv.check_and(check_float, check_temperature), 0.1),
    cfgv.Optional("top_probability", cfgv.check_and(check_float, check_top_probability), 1.0),
    cfgv.NoAdditionalKeys(("api", "model", "temperature", "top_probability")),
)

OPTIONS_NO_DEFAULT_DICT = Map(
    None,
    None,
    *(
        cfgv.OptionalNoDefault(item.key, item.check_fn)
        for item in OPTIONS_DICT.items
        if issubclass(type(item), cfgv.Optional)
    ),
    *(item for item in OPTIONS_DICT.items if not issubclass(type(item), cfgv.Optional)),
)

OUTPUT_DICT = cfgv.Map(
    "output",
    None,
    cfgv.Optional("stream", cfgv.check_bool, True),
    cfgv.Optional("formatted", cfgv.check_bool, True),
    cfgv.Optional("color", cfgv.check_and(cfgv.check_string, check_color), "blue"),
    cfgv.Optional("theme", cfgv.check_string, "dracula"),
    cfgv.NoAdditionalKeys(("stream", "formatted", "color", "theme")),
)

OUTPUT_DICT_NO_DEFAULTS = Map(
    None,
    None,
    *(
        cfgv.OptionalNoDefault(item.key, item.check_fn)
        for item in OUTPUT_DICT.items
        if issubclass(type(item), cfgv.Optional)
    ),
    *(item for item in OUTPUT_DICT.items if not issubclass(type(item), cfgv.Optional)),
)

DEFAULT_DICT = cfgv.Map(
    None,
    None,
    cfgv.OptionalNoDefault("role", cfgv.check_string),
    cfgv.OptionalRecurse("options", OPTIONS_DICT, {}),
    cfgv.OptionalRecurse("output", OUTPUT_DICT, {}),
    cfgv.NoAdditionalKeys(("role", "options", "output")),
)

BUILTIN_ROLES_DICT = cfgv.Map(
    "builtin_roles",
    None,
    cfgv.OptionalRecurse(
        "code",
        cfgv.Map(
            None,
            None,
            cfgv.OptionalRecurse("options", OPTIONS_NO_DEFAULT_DICT, {}),
            cfgv.NoAdditionalKeys(("options",)),
        ),
        {},
    ),
    cfgv.OptionalRecurse(
        "shell",
        cfgv.Map(
            None,
            None,
            cfgv.OptionalRecurse("options", OPTIONS_NO_DEFAULT_DICT, {}),
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
            cfgv.OptionalRecurse("options", OPTIONS_NO_DEFAULT_DICT, {}),
            cfgv.NoAdditionalKeys(("options",)),
        ),
        {},
    ),
)

ROLE_DICT = cfgv.Map(
    "role",
    None,
    cfgv.Required("name", cfgv.check_and(cfgv.check_string, check_role_name)),
    cfgv.Required("description", cfgv.check_string),
    cfgv.OptionalRecurse("options", OPTIONS_NO_DEFAULT_DICT, {}),
    cfgv.OptionalRecurse("output", OUTPUT_DICT_NO_DEFAULTS, {}),
    cfgv.NoAdditionalKeys(
        (
            "name",
            "description",
            "options",
            "output",
        ),
    ),
)

CONFIG_SCHEMA = cfgv.Map(
    "configuration",
    None,
    cfgv.OptionalRecurse(
        "apis",
        APIS_DICT,
        {},
    ),
    cfgv.OptionalRecurse(
        "misc",
        MISC_DICT,
        {},
    ),
    cfgv.OptionalRecurse(
        "default",
        DEFAULT_DICT,
        {},
    ),
    cfgv.OptionalRecurse(
        "builtin_roles",
        BUILTIN_ROLES_DICT,
        {},
    ),
    cfgv.OptionalRecurse(
        "roles",
        Array(ROLE_DICT),
        [],
    ),
    cfgv.NoAdditionalKeys(
        (
            "apis",
            "misc",
            "default",
            "builtin_roles",
            "roles",
        ),
    ),
)
