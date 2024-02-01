from __future__ import annotations

import json
from io import StringIO
from typing import TYPE_CHECKING, Any, TypeVar

import pydantic
import ruamel.yaml
from pydantic import BaseModel

if TYPE_CHECKING:
    from pathlib import Path

    from ruamel.yaml import StreamTextType, StreamType


class YAML(ruamel.yaml.YAML):
    def __init__(self) -> None:
        super().__init__()
        self.indent(mapping=2, sequence=4, offset=2)
        self.width = 100000
        self.default_flow_style = False
        self.allow_unicode = True
        self.pure = True
        self.typ = "safe"


def yaml_load(stream: Path | StreamTextType) -> Any:
    return YAML().load(stream)


def yaml_dump(data: Path | StreamType, stream: Any = None, *, transform: Any = None) -> Any:
    return YAML().dump(data=data, stream=stream, transform=transform)


def yaml_dump_str(data: Path | StreamType, *, transform: Any = None) -> Any:
    stream = StringIO()
    yaml_dump(data=data, stream=stream, transform=transform)
    return stream.getvalue()


T = TypeVar("T", bound=BaseModel)


def from_yaml_file(model_type: type[T], file: Path) -> T:
    return pydantic.TypeAdapter(model_type).validate_python(yaml_load(file.resolve()))


def to_yaml_file(
    file: Path,
    model: BaseModel | Any,
) -> None:
    yaml_dump(json.loads(model.model_dump_json()), file.resolve())
