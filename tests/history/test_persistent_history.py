import pytest

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.history.persistent_history import PersistentHistory


@pytest.fixture()
def persistent_history(mocker, mock_chat_session, tmp_dir_factory):
    persistent_history = PersistentHistory("test_chat_id", 100, tmp_dir_factory.get())
    mocker.patch.object(persistent_history, "_chat_session", mock_chat_session)
    return persistent_history


class TestPersistentHistory:
    def test_get_messages(self, persistent_history, mock_chat_session):
        messages = [{"user": "test_user", "content": "test_content"}]
        mock_chat_session.get_messages.return_value = messages

        result = persistent_history.get_messages()

        assert messages == result

    def test_process_messages(self, persistent_history, mock_chat_session):
        messages = [{"user": "test_user", "content": "test_content"}]

        persistent_history.process_messages(messages)

        mock_chat_session.write_messages.assert_called_once_with(messages)

    def test_print_history(self, persistent_history, mock_chat_session, mocker):
        mock_chat_session.exists.return_value = True

        mock = mocker.patch(f"{C.PROJECT_MODULE}.history.persistent_history.rich_print")

        persistent_history.print_history()

        mock.assert_called()
        mock_chat_session.show_messages.assert_called_once_with(persistent_history._chat_session)
