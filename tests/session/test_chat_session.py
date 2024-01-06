import pytest

from cortex_shell.session.chat_session_manager import ChatSession
from cortex_shell.types import Message


@pytest.fixture()
def chat_session(tmp_dir_factory):
    return ChatSession(file_path=tmp_dir_factory.get() / "test.yaml", size=10)


class TestChatSession:
    def test_exists(self, chat_session):
        assert not chat_session.exists()

    def test_messages(self, chat_session):
        assert chat_session.messages() == []

    def test_write_messages(self, chat_session):
        messages = [Message(role="user", content="Hello")]
        chat_session.write_messages(messages)
        assert chat_session.messages() == messages

    def test_delete(self, chat_session):
        messages = [Message(role="user", content="Hello")]
        chat_session.write_messages(messages)
        assert chat_session.exists()
        chat_session.delete()
        assert not chat_session.exists()

    def test_get_role_name(self, chat_session):
        assert chat_session.get_role_name() is None

    def test_set_role(self, chat_session, mocker):
        role = mocker.Mock()
        role.name = "test_role"
        role.description = "Test role description"
        chat_session.set_role(role)
        assert chat_session.get_role_name() == "test_role"
        assert chat_session.get_system_prompt() == "Test role description"

    def test_get_system_prompt(self, chat_session):
        assert not chat_session.get_system_prompt()
