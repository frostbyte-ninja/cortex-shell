import pytest

from cortex_shell.processing.default_processing import DefaultProcessing


@pytest.fixture
def default_processing(mock_role, mock_history, mock_post_processing):
    return DefaultProcessing(mock_role, mock_history, mock_post_processing)


class TestDefaultProcessing:
    def test_messages(self, mock_history, default_processing):
        mock_history.messages.return_value = []

        prompt = "Test prompt"

        messages = default_processing.get_messages(prompt)

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == default_processing._role.description
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == prompt

    def test_post_processing(self, mock_history, mock_post_processing, default_processing):
        messages = [{"role": "user", "content": "Test message"}]

        default_processing.postprocessing(messages)

        mock_history.process_messages.assert_called_once_with(messages)
        mock_post_processing.assert_called_once_with(messages)

    def test_print_history(self, mock_history, default_processing):
        default_processing.print_history()

        mock_history.print_history.assert_called_once()
