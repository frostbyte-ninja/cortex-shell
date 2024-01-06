import click
import pytest
import typer

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.session.chat_session import ChatSession
from cortex_shell.session.chat_session_manager import ChatSessionManager
from cortex_shell.types import Message


@pytest.fixture()
def chat_session_manager(tmp_dir_factory):
    return ChatSessionManager(storage_path=tmp_dir_factory.get(), history_size=10)


class TestChatSession:
    def test_show_chat_callback(self, mocker, chat_session_manager):
        exists_mock = mocker.patch(f"{C.PROJECT_MODULE}.session.chat_session.ChatSession.exists", return_value=True)
        print_messages_mock = mocker.patch(
            f"{C.PROJECT_MODULE}.session.chat_session_manager.ChatSessionManager.print_messages",
        )

        with pytest.raises(typer.Exit):
            chat_session_manager.show_chat_callback("chat_id")

        exists_mock.assert_called_once()
        print_messages_mock.assert_called_once()

    def test_show_chat_callback_no_chat(self, mocker, chat_session_manager):
        exists_mock = mocker.patch(f"{C.PROJECT_MODULE}.session.chat_session.ChatSession.exists", return_value=False)
        print_messages_mock = mocker.patch(
            f"{C.PROJECT_MODULE}.session.chat_session_manager.ChatSessionManager.print_messages",
        )

        with pytest.raises(click.UsageError):
            chat_session_manager.show_chat_callback("chat_id")

        exists_mock.assert_called_once()
        print_messages_mock.assert_not_called()

    def test_delete_chat_callback(self, mocker, chat_session_manager):
        exists_mock = mocker.patch(f"{C.PROJECT_MODULE}.session.chat_session.ChatSession.exists", return_value=True)
        delete_mock = mocker.patch(f"{C.PROJECT_MODULE}.session.chat_session.ChatSession.delete")

        with pytest.raises(typer.Exit):
            chat_session_manager.delete_chat_callback("chat_id")

        exists_mock.assert_called_once()
        delete_mock.assert_called_once()

    def test_delete_chat_callback_no_chat(self, mocker, chat_session_manager):
        exists_mock = mocker.patch(f"{C.PROJECT_MODULE}.session.chat_session.ChatSession.exists", return_value=False)
        delete_mock = mocker.patch(f"{C.PROJECT_MODULE}.session.chat_session.ChatSession.delete")

        with pytest.raises(click.UsageError):
            chat_session_manager.delete_chat_callback("chat_id")

        exists_mock.assert_called_once()
        delete_mock.assert_not_called()

    def test_clear_chats_callback(self, mocker, chat_session_manager):
        manager_mock = mocker.patch(f"{C.PROJECT_MODULE}.session.chat_session_manager.ChatSessionManager")

        with pytest.raises(typer.Exit):
            chat_session_manager.clear_chats_callback("value")

        manager_mock.assert_called_once()
        manager_mock.return_value.clear_chats.assert_called_once()

    def test_list_chats_callback(self, mocker, chat_session_manager):
        manager_mock = mocker.patch(f"{C.PROJECT_MODULE}.session.chat_session_manager.ChatSessionManager")

        with pytest.raises(typer.Exit):
            chat_session_manager.list_chats_callback("value")

        manager_mock.assert_called_once()
        manager_mock.return_value.print_chats.assert_called_once()

    def test_print_chats(self, tmp_path, mocker, chat_session_manager):
        chat_session_manager._storage_path = tmp_path

        prompt1 = "prompt1"
        chat1 = ChatSession(tmp_path / "chat1.yaml")
        chat1.write_messages([Message(role="user", content=prompt1)])
        chat2 = ChatSession(tmp_path / "chat2.yaml")
        prompt2 = "prompt2"
        chat2.write_messages([Message(role="user", content=prompt2)])

        typer_secho_mock = mocker.patch("typer.secho")
        typer_echo_mock = mocker.patch("typer.echo")

        chat_session_manager.print_chats()

        echo_args = {call.args[0].strip() for call in typer_echo_mock.call_args_list}
        assert chat1.chat_id() in echo_args
        assert chat2.chat_id() in echo_args

        secho_args = {call.args[0].strip() for call in typer_secho_mock.call_args_list}
        assert prompt1 in secho_args
        assert prompt2 in secho_args

        assert "(2)" in secho_args

    def test_print_chats_no_user_prompt(self, tmp_path, mocker, chat_session_manager):
        chat_session_manager._storage_path = tmp_path

        prompt1 = "prompt1"
        chat1 = ChatSession(tmp_path / "chat1.yaml")
        chat1.write_messages([Message(role="system", content=prompt1)])
        chat2 = tmp_path / "chat2.yaml"
        chat2.touch()

        typer_secho_mock = mocker.patch("typer.secho")
        typer_echo_mock = mocker.patch("typer.echo")

        chat_session_manager.print_chats()

        echo_args = {call.args[0].strip() for call in typer_echo_mock.call_args_list}
        assert chat1.chat_id() not in echo_args

        secho_args = {call.args[0].strip() for call in typer_secho_mock.call_args_list}
        assert prompt1 not in secho_args

        assert "(0)" in secho_args

    def test_print_chats_no_chats(self, mocker, chat_session_manager):
        typer_echo_mock = mocker.patch("typer.echo")
        typer_secho_mock = mocker.patch("typer.secho")

        mocker.patch(
            "cortex_shell.session.chat_session_manager.ChatSessionManager.as_list",
            return_value=[],
        )

        chat_session_manager.print_chats()

        typer_echo_mock.assert_called()
        typer_secho_mock.assert_called()

    def test_print_messages(self, mocker, mock_chat_session):
        mock_chat_session.messages.return_value = [
            Message(role="user", content="User message"),
            Message(role="assistant", content="Assistant message"),
        ]

        typer_secho_mock = mocker.patch("typer.secho")

        ChatSessionManager.print_messages(mock_chat_session)

        user_calls = [call.args[0].strip() for call in typer_secho_mock.call_args_list]
        assert "User message" in user_calls
        assert "Assistant message" in user_calls
