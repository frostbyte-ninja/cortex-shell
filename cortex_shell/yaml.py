from __future__ import annotations

import functools
from pathlib import PosixPath, WindowsPath
from typing import TYPE_CHECKING, Any

import cfgv
import yaml

if TYPE_CHECKING:  # pragma: no cover
    from .types import StringConvertible

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:  # pragma: no cover
    from yaml import Dumper, Loader

yaml_load = functools.partial(yaml.load, Loader=Loader)

yaml_dump = functools.partial(
    yaml.dump,
    Dumper=Dumper,
    default_flow_style=False,
    allow_unicode=True,
    indent=2,
    sort_keys=False,
    width=100000,
)


def get_default_from_schema(schema: Any) -> Any:
    return cfgv.apply_defaults({}, schema)


def as_string_representer(dumper: Any, data: StringConvertible) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data))


def none_representer(dumper: Any, _value: Any) -> yaml.ScalarNode:
    # write None as nothing, instead of 'null'
    return dumper.represent_scalar("tag:yaml.org,2002:null", "")


def string_representer(dumper: Any, data: str | None) -> yaml.Node:
    # write nothing, instead of '{}'
    if not data:
        return dumper.represent_scalar("tag:yaml.org,2002:null", "")
    else:
        return dumper.represent_str(data)


def dict_representer(dumper: Any, data: dict[Any, Any]) -> yaml.Node:
    # write nothing, instead of '{}'
    if not data:
        return dumper.represent_scalar("tag:yaml.org,2002:null", "")
    else:
        return dumper.represent_dict(data)


def list_representer(dumper: Any, data: list[Any]) -> yaml.Node:
    # write nothing, instead of '[]'
    if not data:
        return dumper.represent_scalar("tag:yaml.org,2002:null", "")
    else:
        return dumper.represent_list(data)


yaml.add_representer(PosixPath, as_string_representer, Dumper)
yaml.add_representer(WindowsPath, as_string_representer, Dumper)
yaml.add_representer(type(None), none_representer, Dumper)
yaml.add_representer(str, string_representer, Dumper)
yaml.add_representer(dict, dict_representer, Dumper)
yaml.add_representer(list, list_representer, Dumper)
