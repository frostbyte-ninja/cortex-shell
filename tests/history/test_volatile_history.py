import pytest

from cortex_shell.history.volatile_history import VolatileHistory


@pytest.fixture()
def volatile_history():
    return VolatileHistory()


class TestVolatileHistory:
    def test_get_messages_empty(self, volatile_history):
        messages = volatile_history.get_messages()
        assert messages == []

    def test_process_messages(self, volatile_history):
        messages = [{"user": "test_user", "content": "test_content"}]
        volatile_history.process_messages(messages)
        assert volatile_history.get_messages() == messages

    def test_print(self, volatile_history):
        assert volatile_history.print_history() is None

    def test_replace_messages(self, volatile_history):
        messages1 = [{"user": "test_user1", "content": "test_content1"}]
        messages2 = [{"user": "test_user2", "content": "test_content2"}]
        volatile_history.process_messages(messages1)
        volatile_history.process_messages(messages2)
        assert volatile_history.get_messages() == messages2
