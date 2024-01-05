from pathlib import Path

from cortex_shell.cache import Cache


def drain_generator(generator):
    return "".join(generator)


class TestCache:
    def test_with_cache(self, mocker, tmp_dir_factory):
        cache_path = Path(tmp_dir_factory.get())
        cache = Cache(5, cache_path)

        mock_function = mocker.MagicMock(return_value="result")
        function = cache(mock_function)

        result = drain_generator(function(caching=True, messages=[]))
        drain_generator(function(caching=True, messages=[]))
        drain_generator(function(caching=True, messages=[]))

        cached_files = list(cache_path.glob("*"))

        assert len(cached_files) == 1
        assert mock_function.call_count == 1
        assert result == "result"

    def test_without_cache(self, mocker, tmp_dir_factory):
        cache_path = Path(tmp_dir_factory.get())
        cache = Cache(5, cache_path)

        mock_function = mocker.MagicMock(return_value="result")
        function = cache(mock_function)

        result = drain_generator(function(caching=False, messages=[]))
        drain_generator(function(caching=False, messages=[]))
        drain_generator(function(caching=False, messages=[]))
        cached_files = list(cache_path.glob("*"))

        assert len(cached_files) == 1
        assert mock_function.call_count == 3
        assert result == "result"

    def test_multiple_requests(self, mocker, tmp_dir_factory):
        cache_path = Path(tmp_dir_factory.get())
        cache = Cache(10, cache_path)

        @cache
        def function(*_args, **kwargs):
            return ""

        drain_generator(function(caching=True, messages=[]))
        drain_generator(function(caching=True, param1=None, messages=[]))
        drain_generator(function(caching=True, param2=None, messages=[]))
        drain_generator(function(caching=True, param3=None, messages=[]))
        drain_generator(function(caching=True, param3=None, messages=["123"]))

        cached_files = list(cache_path.glob("*"))
        assert len(cached_files) == 5

    def test_cache_limit(self, tmp_dir_factory):
        cache_path = Path(tmp_dir_factory.get())
        cache = Cache(2, cache_path)

        @cache
        def function(*_args, **kwargs):
            return ""

        drain_generator(function(caching=True, messages=[]))
        drain_generator(function(caching=True, param1=None, messages=[]))
        drain_generator(function(caching=True, param2=None, messages=[]))

        cached_files = list(cache_path.glob("*"))
        assert len(cached_files) == 2
