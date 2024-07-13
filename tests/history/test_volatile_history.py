import pytest

from cortex_shell.history.volatile_history import VolatileHistory
from cortex_shell.types import Message


@pytest.fixture
def volatile_history():
    return VolatileHistory()


class TestVolatileHistory:
    def test_messages_empty(self, volatile_history):
        messages = volatile_history.messages()
        assert messages == []

    def test_process_messages(self, volatile_history):
        messages = [Message(role="test_user", content="test_content")]
        volatile_history.process_messages(messages)
        assert volatile_history.messages() == messages

    def test_print(self, volatile_history):
        assert volatile_history.print_history() is None

    def test_replace_messages(self, volatile_history):
        messages1 = [Message(role="test_user1", content="test_content1")]
        messages2 = [Message(role="test_user2", content="test_content2")]
        volatile_history.process_messages(messages1)
        volatile_history.process_messages(messages2)
        assert volatile_history.messages() == messages2
