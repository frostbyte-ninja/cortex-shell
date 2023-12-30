from cortex_shell.post_processing.no_post_processing import NoPostProcessing


class TestNoPostProcessing:
    def test_no_post_processing(self):
        messages = [
            {"content": "Message 1"},
            {"content": "Message 2"},
            {"content": "Message 3"},
        ]

        no_post_processing = NoPostProcessing()

        no_post_processing(messages)
