import stat
import sys
from importlib import import_module, reload
from pathlib import Path

import pytest
import typer

from cortex_shell import constants as C  # noqa: N812
from cortex_shell.client.iclient import IClient
from cortex_shell.configuration.config import Config, cfg, set_cfg
from cortex_shell.configuration.schema import BuiltinRoleShell, Options, Output, Role
from cortex_shell.history.ihistory import IHistory
from cortex_shell.post_processing.ipost_processing import IPostProcessing
from cortex_shell.processing.iprocessing import IProcessing
from cortex_shell.renderer.irenderer import IRenderer
from cortex_shell.session.chat_session import ChatSession
from cortex_shell.session.chat_session_manager import ChatSessionManager
from cortex_shell.util import install_shell_integration
from cortex_shell.yaml import to_yaml_file


@pytest.fixture(autouse=True)
def _mock_configuration(tmp_dir_factory, monkeypatch):
    tmp_dir = tmp_dir_factory.get()
    monkeypatch.setenv("HOME", str(tmp_dir.as_posix()))
    monkeypatch.setenv("USERPROFILE", str(tmp_dir))
    monkeypatch.setenv("HOMEDRIVE", "")
    monkeypatch.setenv("HOMEPATH", str(tmp_dir))

    # reload Configuration
    reload(import_module(f"{C.PROJECT_MODULE}.configuration.schema"))
    reload(import_module(f"{C.PROJECT_MODULE}.configuration.config"))

    set_cfg(Config())


@pytest.fixture()
def configuration_override(_mock_configuration):
    def _apply_config_changes(config_changes, config_instance=None):
        config = config_instance if config_instance is not None else cfg().model

        for key_path, value in config_changes.items():
            attribute = config
            for key in key_path[:-1]:
                attribute = getattr(attribute, key)
            setattr(attribute, key_path[-1], value)

        to_yaml_file(cfg().config_file(), config)
        set_cfg(Config(cfg().config_directory()))

    return _apply_config_changes


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
    options = Options(api="chatgpt", model="test_model1", temperature=0.5, top_probability=0.7)
    output = Output(stream=True, formatted=False, color="blue", theme="dark")
    return Role(name="role1", description="description1", options=options, output=output)


@pytest.fixture()
def mock_shell_role():
    options = Options(api="chatgpt", model="test_model2", temperature=0.8, top_probability=0.9)
    output = Output(stream=False, formatted=True, color="red", theme="green")
    return BuiltinRoleShell(
        name="role2",
        description="description2",
        options=options,
        output=output,
        default_execute=True,
    )


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
