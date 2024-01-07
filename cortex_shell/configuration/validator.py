from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import cfgv
import validators
from pathvalidate import validate_filepath

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path


def check_greater_than_zero(value: int) -> None:
    if value <= 0:
        raise cfgv.ValidationError(f"{value} is not greater than 0")


def check_type_optional(tp: type, typename: str | None = None) -> Callable[[Any], None]:
    # TODO(fn): remove this function when python 3.9 gets deprecated
    # check_str = cfgv.check_type(Optional[str]) will work fine then
    def check_type_optional_fn(v: Any) -> None:
        if v is not None and not isinstance(v, tp):
            typename_s = typename or tp.__name__
            raise cfgv.ValidationError(
                f"Expected {typename_s} got {type(v).__name__}",
            )

    return check_type_optional_fn


def check_path(path: str | Path) -> None:
    try:
        validate_filepath(path, platform="auto")
    except Exception as e:
        raise cfgv.ValidationError(f"{path!r} is not a valid path") from e


def check_api(api: str) -> None:
    supported_apis = {"chatgpt"}

    if api not in supported_apis:
        raise cfgv.ValidationError(f'"{api}" API is not supported. Valid options are "' + ", ".join(supported_apis))


def check_color(color: str) -> None:
    low_intensity = {"black", "red", "green", "yellow", "blue", "magenta", "cyan", "gray"}
    high_intensity = {
        "brightblack",
        "brightred",
        "brightgreen",
        "brightyellow",
        "brightblue",
        "brightmagenta",
        "brightcyan",
        "white",
    }
    all_colors = {*low_intensity, *high_intensity}
    if color not in all_colors:
        options = ", ".join(all_colors)
        raise cfgv.ValidationError(f'"{color}" is not a supported color. Valid options are: {options}')


def check_url_optional(url: str | None) -> None:
    if url is not None and not validators.url(url):
        raise cfgv.ValidationError(f'"{url}" is not a valid url') from None


def check_temperature(value: float) -> None:
    if value < 0.0 or value > 2.0:  # noqa: PLR2004
        raise cfgv.ValidationError(f'"{value}" is not in the valid temperature range of 0.0<=x<=2.0')


def check_top_probability(value: float) -> None:
    if value < 0.0 or value > 1.0:  # noqa: PLR2004
        raise cfgv.ValidationError(f'"{value}" is not in the valid top_probability range of 0.0<=x<=1.0')


def check_role_name(role_id: str) -> None:
    invalid_ids = ["default", "code", "shell", "describe_shell"]
    if role_id in invalid_ids:
        raise cfgv.ValidationError("id must be none of: " + ", ".join(invalid_ids))


check_float = cfgv.check_type(float)
check_str_optional = check_type_optional(str)
