from cortex_shell.post_processing.no_post_processing import NoPostProcessing
from cortex_shell.types import Message


class TestNoPostProcessing:
    def test_no_post_processing(self):
        messages = [
            Message(role="test_user", content="Message 1"),
            Message(role="test_user", content="Message 2"),
            Message(role="test_user", content="Message 3"),
        ]

        no_post_processing = NoPostProcessing()

        no_post_processing(messages)
