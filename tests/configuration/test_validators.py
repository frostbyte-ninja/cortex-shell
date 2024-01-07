import cfgv
import pytest

from cortex_shell.configuration.validator import (
    check_api,
    check_color,
    check_greater_than_zero,
    check_path,
    check_role_name,
    check_temperature,
    check_top_probability,
    check_type_optional,
    check_url_optional,
)


class TestValidators:
    def test_check_greater_than_zero(self):
        check_greater_than_zero(1)
        with pytest.raises(cfgv.ValidationError):
            check_greater_than_zero(0)

    def test_check_type_optional(self):
        check_str_optional_fn = check_type_optional(str)
        check_str_optional_fn("test")
        check_str_optional_fn(None)
        with pytest.raises(cfgv.ValidationError):
            check_str_optional_fn(1)

    def test_check_path(self):
        check_path("test.txt")
        with pytest.raises(cfgv.ValidationError):
            check_path("\0")

    def test_check_api(self):
        check_api("chatgpt")
        with pytest.raises(cfgv.ValidationError):
            check_api("unsupported")

    def test_check_color(self):
        check_color("red")
        with pytest.raises(cfgv.ValidationError):
            check_color("unsupported")

    def test_check_url(self):
        check_url_optional("https://example.com")
        check_url_optional(None)
        with pytest.raises(cfgv.ValidationError):
            check_url_optional("invalid_url")

    def test_check_temperature(self):
        check_temperature(1.0)
        with pytest.raises(cfgv.ValidationError):
            check_temperature(-0.1)
        with pytest.raises(cfgv.ValidationError):
            check_temperature(2.1)

    def test_check_top_probability(self):
        check_top_probability(0.5)
        with pytest.raises(cfgv.ValidationError):
            check_top_probability(-0.1)
        with pytest.raises(cfgv.ValidationError):
            check_top_probability(1.1)

    def test_check_role_name(self):
        check_role_name("custom_role")
        with pytest.raises(cfgv.ValidationError):
            check_role_name("default")
