import pytest

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.renderer.plain_renderer import PlainRenderer


@pytest.fixture()
def plain_renderer(mock_role):
    return PlainRenderer(mock_role)


class TestPlainRenderer:
    def test_enter(self, mocker, plain_renderer):
        mock = mocker.patch(f"{C.PROJECT_MODULE}.renderer.plain_renderer.print_formatted_text")

        with plain_renderer:
            mock.assert_not_called()

    def test_exit(self, mocker, plain_renderer):
        mock = mocker.patch(f"{C.PROJECT_MODULE}.renderer.plain_renderer.print_formatted_text")

        with plain_renderer:
            pass

        mock.assert_called_once()

    def test_call(self, mocker, plain_renderer):
        print_formatted_text_mock = mocker.patch(f"{C.PROJECT_MODULE}.renderer.plain_renderer.print_formatted_text")
        colored_text_mock = mocker.patch(f"{C.PROJECT_MODULE}.renderer.plain_renderer.get_colored_text")

        with plain_renderer as renderer:
            renderer("text1", "text2")

        print_formatted_text_mock.assert_any_call(mocker.ANY, end="")
        colored_text_mock.assert_called_with("text2", mocker.ANY)
