from collections.abc import Generator
from hashlib import md5
from pathlib import Path
from typing import Any, Callable

from .configuration import cfg
from .util import option_callback, rmtree
from .yaml import yaml_dump_str


class Cache:
    """
    Decorator class that adds caching functionality to a function.
    """

    def __init__(self, size: int, cache_path: Path) -> None:
        """
        Initialize the Cache decorator.

        :param size: Integer, maximum number of cache files to keep.
        """
        self._size = size
        self._cache_path = cache_path
        self._cache_path.mkdir(parents=True, exist_ok=True)

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        The Cache decorator.

        :param func: The function to cache.
        :return: Wrapped function with caching.
        """

        def wrapper(*args: Any, **kwargs: Any) -> Generator[str, None, None]:
            cache_file = self._cache_path / self._get_hash_from_request(**kwargs)
            if kwargs.pop("caching", False) and cache_file.exists():
                yield cache_file.read_text(encoding="utf-8")
            else:
                result = ""
                for chunk in func(*args, **kwargs):
                    result += chunk
                    yield chunk
                cache_file.write_text(result, encoding="utf-8")
                self._delete_oldest_files(self._size)

        return wrapper

    def _delete_oldest_files(self, max_files: int) -> None:
        """
        Class method to delete the oldest cached files in the CACHE_DIR folder.

        :param max_files: Integer, the maximum number of files to keep in the CACHE_DIR folder.
        """
        # Get all files in the folder.
        files = list(self._cache_path.glob("*"))
        # Sort files by last modification time in ascending order.
        files = sorted(files, key=lambda f: f.stat().st_mtime)
        # Delete the oldest files if the number of files exceeds the limit.
        if len(files) > max_files:
            num_files_to_delete = len(files) - max_files
            for i in range(num_files_to_delete):
                files[i].unlink()

    @staticmethod
    def _get_hash_from_request(**kwargs: Any) -> str:
        kwargs.pop("caching")
        # delete every message except the last one, which is the most recent user prompt
        kwargs["messages"] = kwargs["messages"][-1:]
        return md5(yaml_dump_str(kwargs).encode("utf-8")).hexdigest()

    @classmethod
    @option_callback
    def clear_cache_callback(cls, *_args: Any) -> None:
        rmtree(cfg().config.misc.session.chat_cache_path)
