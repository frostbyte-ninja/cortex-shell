from cortex_shell.post_processing.file_output_post_processing import FileOutputPostProcessing


class TestFileOutputPostProcessing:
    def test_file_output_post_processing(self, tmp_file_factory):
        file = tmp_file_factory.get()

        messages = [
            {"content": "Message 1"},
            {"content": "Message 2"},
            {"content": "Message 3"},
        ]

        file_output_post_processing = FileOutputPostProcessing(file)
        file_output_post_processing(messages)
        file_content = file.read_text(encoding="utf-8")

        assert file_content == "Message 3"
