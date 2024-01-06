import stat
import sys
from pathlib import Path

import pytest
import typer
import yaml

from cortex_shell import configuration
from cortex_shell import constants as C  # noqa: N812
from cortex_shell.client.iclient import IClient
from cortex_shell.configuration.config import Config, _get_default_directory, set_cfg
from cortex_shell.history.ihistory import IHistory
from cortex_shell.post_processing.ipost_processing import IPostProcessing
from cortex_shell.processing.iprocessing import IProcessing
from cortex_shell.renderer.irenderer import IRenderer
from cortex_shell.role import Options, Output, Role, ShellRole
from cortex_shell.session.chat_session import ChatSession
from cortex_shell.session.chat_session_manager import ChatSessionManager
from cortex_shell.util import install_shell_integration


@pytest.fixture(autouse=True)
def _mock_home_and_default_configuration(tmp_dir_factory, monkeypatch):
    tmp_dir = tmp_dir_factory.get()
    monkeypatch.setenv("HOME", str(tmp_dir.as_posix()))
    monkeypatch.setenv("USERPROFILE", str(tmp_dir))
    monkeypatch.setenv("HOMEDRIVE", "")
    monkeypatch.setenv("HOMEPATH", str(tmp_dir))
    config = configuration.config.Config(tmp_dir)
    set_cfg(config)


@pytest.fixture()
def _no_stdin(mocker):
    for module_name, module in sys.modules.items():
        if hasattr(module, "has_stdin"):
            mocker.patch(f"{module_name}.has_stdin", return_value=False)


@pytest.fixture()
def _stdin(mocker):
    for module_name, module in sys.modules.items():
        if hasattr(module, "has_stdin"):
            mocker.patch(f"{module_name}.has_stdin", return_value=True)
        if hasattr(module, "get_stdin"):
            mocker.patch(f"{module_name}.get_stdin", return_value="Some Text")


@pytest.fixture()
def mock_typer_prompt(mocker):
    return mocker.patch("typer.prompt")


@pytest.fixture()
def tmp_dir_factory(tmp_path):
    class TmpDirFactory:
        def __init__(self) -> None:
            self.tmp_dir_count = 0

        def get(self) -> Path:
            path = tmp_path / f"dir{self.tmp_dir_count}"
            self.tmp_dir_count += 1
            path.mkdir()
            return path

    return TmpDirFactory()


@pytest.fixture()
def tmp_file_factory(tmp_path):
    class TmpFileFactory:
        def __init__(self) -> None:
            self.tmp_dir_count = 0

        def get(self) -> Path:
            path = tmp_path / str(self.tmp_dir_count)
            self.tmp_dir_count += 1
            path.touch()
            return path

    return TmpFileFactory()


@pytest.fixture()
def mock_role():
    options = Options(api="test_api1", model="test_model1", temperature=0.5, top_probability=0.7)
    output = Output(stream=True, formatted=False, color="blue", theme="dark")
    return Role("role1", "description1", options, output)


@pytest.fixture()
def mock_shell_role():
    options = Options(api="test_api2", model="test_model2", temperature=0.8, top_probability=0.9)
    output = Output(stream=False, formatted=True, color="red", theme="green")
    return ShellRole("role2", "description2", True, options, output)


@pytest.fixture()
def mock_config_with_env_override(tmp_dir_factory, monkeypatch):
    def _apply_env_override(**env_vars):
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)
        config = Config(tmp_dir_factory.get())
        set_cfg(config)

    return _apply_env_override


@pytest.fixture()
def mock_config_with_values(tmp_dir_factory):
    def _create_existing_config_file(config_dict):
        config_dir = _get_default_directory()
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / C.CONFIG_FILE
        with config_file.open("w") as f:
            yaml.dump(config_dict, f)
        config = Config()
        set_cfg(config)

    return _create_existing_config_file


@pytest.fixture()
def mock_shell_integration(mocker):
    def _install(shell: str) -> None:
        mocker.patch(f"{C.PROJECT_MODULE}.util.shell_name", return_value=shell)
        with pytest.raises(typer.Exit):
            install_shell_integration(None, "x")

    return _install


@pytest.fixture()
def mock_executable(tmp_dir_factory):
    path = tmp_dir_factory.get() / C.PROJECT_NAME
    with path.open("w", encoding="utf-8") as file:
        file.write("echo COMPLETION")
    # make executable
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


@pytest.fixture()
def mock_client(mocker):
    return mocker.MagicMock(spec=IClient)


@pytest.fixture()
def mock_processing(mocker):
    return mocker.MagicMock(spec=IProcessing)


@pytest.fixture()
def mock_renderer(mocker):
    return mocker.MagicMock(spec=IRenderer)


@pytest.fixture()
def mock_chat_session(mocker):
    return mocker.MagicMock(spec=ChatSession)


@pytest.fixture()
def mock_chat_session_manager(mocker, mock_chat_session):
    manager = mocker.MagicMock(spec=ChatSessionManager)
    manager.get_session.return_value = mock_chat_session
    return manager


@pytest.fixture()
def mock_history(mocker):
    return mocker.MagicMock(spec=IHistory)


@pytest.fixture()
def mock_post_processing(mocker):
    return mocker.MagicMock(spec=IPostProcessing)
