from typing import TypeVar, cast

import cfgv

T = TypeVar("T")


class Map(cfgv.Map):
    def check(self, v: T) -> None:
        if v is None:
            return
        super().check(v)

    def apply_defaults(self, v: T) -> T:
        if v is None:
            return {}
        return cast(T, super().apply_defaults(v))

    def remove_defaults(self, v: T) -> T:
        if v is None:
            return {}
        return cast(T, super().remove_defaults(v))


class Array(cfgv.Array[T]):
    def check(self, v: T) -> None:
        if v is None:
            return
        super().check(v)

    def apply_defaults(self, v: T) -> T:
        if v is None:
            return []
        return cast(T, super().apply_defaults(v))

    def remove_defaults(self, v: T) -> T:
        if v is None:
            return []
        return cast(T, super().remove_defaults(v))
