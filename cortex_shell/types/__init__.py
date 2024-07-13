from __future__ import annotations

from typing import TypedDict, Union


class Message(TypedDict):
    role: str
    content: str


YamlType = Union[str, int, float, bool, None, list["YamlType"], dict[str, "YamlType"]]
