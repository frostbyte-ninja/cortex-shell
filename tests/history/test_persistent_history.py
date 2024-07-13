import pytest

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.history.persistent_history import PersistentHistory
from cortex_shell.types import Message


@pytest.fixture
def persistent_history(mock_chat_session_manager):
    return PersistentHistory("test_chat_id", mock_chat_session_manager)


class TestPersistentHistory:
    def test_messages(self, persistent_history, mock_chat_session):
        messages = [Message(role="test_user", content="test_content")]
        mock_chat_session.messages.return_value = messages

        result = persistent_history.messages()

        assert messages == result

    def test_process_messages(self, persistent_history, mock_chat_session):
        messages = [Message(role="test_user", content="test_content")]

        persistent_history.process_messages(messages)

        mock_chat_session.write_messages.assert_called_once_with(messages)

    def test_print_history(self, persistent_history, mock_chat_session, mock_chat_session_manager, mocker):
        mock_chat_session.exists.return_value = True

        mock = mocker.patch(f"{C.PROJECT_MODULE}.history.persistent_history.rich_print")

        persistent_history.print_history()

        mock.assert_called()
        mock_chat_session_manager.print_messages.assert_called_once_with(mock_chat_session)
