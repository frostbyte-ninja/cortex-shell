import itertools
import os
import shutil
from importlib import resources
from pathlib import Path


def all_combinations(*input_values):
    return [
        subset for length in range(1, len(input_values) + 1) for subset in itertools.combinations(input_values, length)
    ]


def get_test_resource_file(resource_name: str, submodule: str = "", relative: bool = True) -> Path:
    module = "testing.resources"
    if submodule:
        module = f"{module}.{submodule}"
    with resources.as_file(resources.files(module) / resource_name) as path:
        if relative:
            return Path(os.path.relpath(path, Path.cwd()))
        else:
            return path


def get_path_to_shell(shell_name: str) -> Path:
    def remove_system32_from_path(path: str) -> str:
        system32_path = r"C:\Windows\System32".lower()
        path_parts = path.split(os.pathsep)
        return os.pathsep.join(p for p in path_parts if p.lower() != system32_path)

    # C:\Windows\System32\bash.exe resets the HOME variable, which leads to issues during tests
    return Path(shutil.which(shell_name, path=remove_system32_from_path(os.environ["PATH"])))


def prepend_dir_to_path(path: Path, env=None):
    if env is None:
        env = os.environ.copy()
    env["PATH"] = str(path) + os.pathsep + env["PATH"]
    return env
