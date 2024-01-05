import pytest
import typer

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.chat_session import ChatSession
from cortex_shell.types import Message


@pytest.fixture()
def chat_session(tmp_dir_factory):
    return ChatSession(chat_id="test_chat_id", size=10, storage_path=tmp_dir_factory.get())


class TestChatSession:
    def test_init(self, chat_session):
        assert chat_session._chat_id == "test_chat_id"
        assert chat_session._size == 10
        assert chat_session._storage_path.is_dir()

    def test_exists(self, chat_session):
        assert not chat_session.exists()

    def test_delete(self, chat_session):
        chat_session.delete()
        assert not chat_session._get_chat_file_path().exists()

    def test_to_list(self, chat_session):
        assert chat_session.to_list() == []

    def test_get_messages(self, chat_session):
        assert chat_session.get_messages() == []

    def test_write_messages(self, chat_session):
        messages = [Message(role="user", content="Hello")]
        chat_session.write_messages(messages)
        assert chat_session.get_messages() == messages

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

    def test_list_ids_callback(self, mocker):
        list_id_mock = mocker.patch(f"{C.PROJECT_MODULE}.chat_session.ChatSession.list_ids")
        chat_session_mock = mocker.patch(f"{C.PROJECT_MODULE}.chat_session.ChatSession")

        with pytest.raises(typer.Exit):
            ChatSession.list_ids_callback("chat_id")

        chat_session_mock.assert_called_with("chat_id", mocker.ANY, mocker.ANY)
        list_id_mock.assert_called_once()

    def test_show_messages_callback(self, mocker):
        show_messages_mock = mocker.patch(f"{C.PROJECT_MODULE}.chat_session.ChatSession.show_messages")
        chat_session_mock = mocker.patch(f"{C.PROJECT_MODULE}.chat_session.ChatSession")

        with pytest.raises(typer.Exit):
            ChatSession.show_messages_callback("chat_id")

        chat_session_mock.assert_called_with("chat_id", mocker.ANY, mocker.ANY)
        show_messages_mock.assert_called_once()

    def test_delete_messages_callback(self, mocker):
        chat_session_mock = mocker.patch(f"{C.PROJECT_MODULE}.chat_session.ChatSession")

        with pytest.raises(typer.Exit):
            ChatSession.delete_messages_callback("chat_id")

        chat_session_mock.assert_called_with("chat_id", mocker.ANY, mocker.ANY)
        chat_session_mock.return_value.delete.assert_called_once()

    def test_clear_chats_callback(self, mocker):
        rmtree_mock = mocker.patch(f"{C.PROJECT_MODULE}.chat_session.rmtree")
        cfg_mock = mocker.patch(f"{C.PROJECT_MODULE}.chat_session.cfg")

        with pytest.raises(typer.Exit):
            ChatSession.clear_chats_callback("value")

        rmtree_mock.assert_called_once_with(cfg_mock.return_value.chat_history_path.return_value)
