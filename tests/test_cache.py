import pytest

from cortex_shell.cache import Cache


def drain_generator(generator):
    return "".join(generator)


@pytest.fixture()
def cache_path(tmp_dir_factory):
    temp_dir = tmp_dir_factory.get() / "some_dir"
    assert not temp_dir.exists()
    return temp_dir


@pytest.fixture()
def cache(cache_path):
    cache = Cache(5, cache_path)
    assert cache_path.exists()
    return cache


class TestCache:
    def test_with_cache(self, mocker, cache, cache_path):
        mock_function = mocker.MagicMock(return_value="result")
        function = cache(mock_function)

        result = drain_generator(function(caching=True, messages=[]))
        drain_generator(function(caching=True, messages=[]))
        drain_generator(function(caching=True, messages=[]))

        cached_files = list(cache_path.glob("*"))

        assert len(cached_files) == 1
        assert mock_function.call_count == 1
        assert result == "result"

    def test_without_cache(self, mocker, cache, cache_path):
        mock_function = mocker.MagicMock(return_value="result")
        function = cache(mock_function)

        result = drain_generator(function(caching=False, messages=[]))
        drain_generator(function(caching=False, messages=[]))
        drain_generator(function(caching=False, messages=[]))
        cached_files = list(cache_path.glob("*"))

        assert len(cached_files) == 1
        assert mock_function.call_count == 3
        assert result == "result"

    def test_multiple_requests(self, cache, cache_path):
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

    def test_cache_limit(self, cache, cache_path):
        @cache
        def function(*_args, **kwargs):
            return ""

        drain_generator(function(caching=True, messages=[]))
        drain_generator(function(caching=True, param1=None, messages=[]))
        drain_generator(function(caching=True, param2=None, messages=[]))
        drain_generator(function(caching=True, param3=None, messages=[]))
        drain_generator(function(caching=True, param4=None, messages=[]))
        drain_generator(function(caching=True, param5=None, messages=[]))

        cached_files = list(cache_path.glob("*"))
        assert len(cached_files) == 5
