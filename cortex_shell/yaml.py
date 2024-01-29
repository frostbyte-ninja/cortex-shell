from __future__ import annotations

from io import BytesIO, IOBase, StringIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

import pydantic
import ruamel.yaml
from pydantic import BaseModel

if TYPE_CHECKING:
    from ruamel.yaml import StreamTextType, StreamType


class YAML(ruamel.yaml.YAML):
    def __init__(self) -> None:
        super().__init__()
        self.indent(mapping=2, sequence=4, offset=2)
        self.width = 100000
        self.default_flow_style = False
        self.allow_unicode = True
        self.preserve_quotes = True
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


def parse_yaml_raw_as(model_type: type[T], raw: str | bytes | IOBase) -> T:
    stream: IOBase
    if isinstance(raw, str):
        stream = StringIO(raw)
    elif isinstance(raw, bytes):
        stream = BytesIO(raw)
    elif isinstance(raw, IOBase):
        stream = raw
    else:
        raise TypeError(f"Expected str, bytes or IO, but got {raw!r}")
    objects = yaml_load(stream)
    ta = pydantic.TypeAdapter(model_type)
    return ta.validate_python(objects, strict=True)


def parse_yaml_file_as(model_type: type[T], file: Path | str | IOBase) -> T:
    if isinstance(file, IOBase):
        return parse_yaml_raw_as(model_type, raw=file)

    if isinstance(file, str):
        file = Path(file).resolve()
    elif isinstance(file, Path):
        file = file.resolve()
    else:
        raise TypeError(f"Expected Path, str or IO, but got {file!r}")

    with file.open(mode="r") as file:
        return parse_yaml_raw_as(model_type, file)
