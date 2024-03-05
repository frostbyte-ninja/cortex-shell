from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

import pydantic
import ruamel.yaml
from pydantic import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from ruamel.yaml import ScalarNode, StreamTextType, StreamType


class YAML(ruamel.yaml.YAML):
    def __init__(self) -> None:
        super().__init__(typ="safe", pure=True)
        self.indent(mapping=2, sequence=4, offset=2)
        self.width = 100000
        self.default_flow_style = False
        self.allow_unicode = True
        self.representer.sort_base_mapping_type_on_output = False

        self.representer.add_representer(type(None), self._represent_none)

    @staticmethod
    def _represent_none(representer: Any, data: Any) -> ScalarNode:
        return representer.represent_scalar("tag:yaml.org,2002:null", "")


def yaml_load(stream: Path | StreamTextType) -> Any:
    if isinstance(stream, Path):
        with stream.open("r", encoding="utf-8") as file:
            return YAML().load(file)
    else:
        return YAML().load(stream)


def yaml_dump(data: Path | StreamType, stream: Any = None, *, transform: Any = None) -> Any:
    if isinstance(stream, Path):
        with stream.open("w", encoding="utf-8") as file:
            YAML().dump(data=data, stream=file, transform=transform)
    else:
        YAML().dump(data=data, stream=stream, transform=transform)


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
