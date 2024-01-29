import pytest

from cortex_shell.configuration.validator import (
    check_api,
    check_color,
    check_path,
    check_role_name,
    check_url,
)

# ruff: noqa: PT011


class TestValidators:
    def test_check_path(self):
        check_path("test.txt")
        with pytest.raises(ValueError):
            check_path("\0")

    def test_check_api(self):
        check_api("chatgpt")
        with pytest.raises(ValueError):
            check_api("unsupported")

    def test_check_color(self):
        check_color("red")
        with pytest.raises(ValueError):
            check_color("unsupported")

    def test_check_url(self):
        check_url("https://example.com")
        with pytest.raises(ValueError):
            check_url("invalid_url")

    def test_check_role_name(self):
        check_role_name("custom_role")
        with pytest.raises(ValueError):
            check_role_name("default")
