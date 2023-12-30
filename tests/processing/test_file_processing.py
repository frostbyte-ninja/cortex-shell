import pytest

from cortex_shell.processing.file_processing import FileProcessing
from cortex_shell.role import FILE_ROLE


@pytest.fixture()
def file_processing(mock_role, mock_history, mock_post_processing, tmp_file_factory):
    files = [tmp_file_factory.get()]
    return FileProcessing(mock_role, files, mock_history, mock_post_processing)


class TestFileProcessing:
    def test_get_messages(self, tmp_file_factory, mock_role, mock_history, mock_post_processing):
        mock_history.get_messages.return_value = []

        file = tmp_file_factory.get()
        file.write_text("This is a test file.")

        file_processing = FileProcessing(mock_role, [file], mock_history, mock_post_processing)

        prompt = "Test prompt"
        messages = file_processing.get_messages(prompt)

        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == FILE_ROLE
        assert messages[1]["role"] == "user"
        assert file.name in messages[1]["content"]
        assert messages[2]["role"] == "system"
        assert messages[2]["content"] == file_processing._role.description
        assert messages[3]["role"] == "user"
        assert messages[3]["content"] == prompt

    def test_postprocessing(self, file_processing, mock_history, mock_post_processing):
        messages = [{"role": "user", "content": "Test message"}]
        file_processing.postprocessing(messages)

        mock_history.process_messages.assert_called_once_with(messages)
        mock_post_processing.assert_called_once_with(messages)

    def test_print_history(self, file_processing, mock_history):
        file_processing.print_history()
        mock_history.print_history.assert_not_called()
