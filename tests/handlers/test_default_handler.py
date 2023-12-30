import pytest

from cortex_shell.handlers.default_handler import DefaultHandler
from cortex_shell.handlers.ihandler import IHandler


@pytest.fixture()
def default_handler(mock_client, mock_processing, mock_renderer):
    return DefaultHandler(mock_client, mock_processing, mock_renderer)


class TestDefaultHandler:
    def test_default_handler_instance(self, default_handler):
        assert isinstance(default_handler, IHandler)

    def test_handle_calls_processing_methods(self, default_handler, mock_processing):
        prompt = "Test prompt"
        default_handler.handle(prompt)
        mock_processing.get_messages.assert_called_once_with(prompt)
        mock_processing.postprocessing.assert_called_once()

    def test_handle_calls_client_get_completion(self, default_handler, mock_client):
        prompt = "Test prompt"
        default_handler.handle(prompt)
        mock_client.get_completion.assert_called_once()

    def test_handle_returns_response(self, default_handler, mock_client):
        prompt = "Test prompt"
        mock_client.get_completion.return_value = ["Test response"]
        response = default_handler.handle(prompt)
        assert response == "Test response"
