import pytest

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.renderer.formatted_renderer import FormattedRenderer


@pytest.fixture
def formatted_renderer(mock_role):
    return FormattedRenderer(mock_role)


class TestFormattedRenderer:
    def test_enter(self, mocker, formatted_renderer):
        mock = mocker.patch(f"{C.PROJECT_MODULE}.renderer.formatted_renderer.Live")

        with formatted_renderer:
            mock.return_value.__enter__.assert_called_once()

    def test_exit(self, mocker, formatted_renderer):
        mock = mocker.patch(f"{C.PROJECT_MODULE}.renderer.formatted_renderer.Live")

        with formatted_renderer:
            pass

        mock.return_value.__exit__.assert_called_once()

    def test_call(self, mocker, formatted_renderer):
        live_mock = mocker.patch(f"{C.PROJECT_MODULE}.renderer.formatted_renderer.Live")
        markdown_mock = mocker.patch(f"{C.PROJECT_MODULE}.renderer.formatted_renderer.Markdown")

        with formatted_renderer as renderer:
            renderer("text1", "text2")

        live_mock.return_value.update.assert_called_once()
        markdown_mock.assert_called_with("text1text2", code_theme=mocker.ANY, style=mocker.ANY)

    def test_call_no_context(self, mocker, formatted_renderer):
        mock = mocker.patch(f"{C.PROJECT_MODULE}.renderer.formatted_renderer.Live")

        with pytest.raises(RuntimeError):
            formatted_renderer("text1", "text2")

        mock.return_value.update.assert_not_called()
