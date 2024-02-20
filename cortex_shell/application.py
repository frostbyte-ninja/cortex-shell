from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Optional

import click
import typer
from click import ClickException, FileError, UsageError
from identify import identify
from pydantic import ValidationError

from . import errors
from .cache import Cache
from .client.chatgpt_client import ChatGptClient
from .client.iclient import IClient
from .configuration import cfg
from .error_handler import ErrorHandler
from .errors import InvalidConfigError
from .handlers.default_handler import DefaultHandler
from .handlers.ihandler import IHandler
from .handlers.repl_handler import ReplHandler
from .history.ihistory import IHistory
from .history.persistent_history import PersistentHistory
from .history.volatile_history import VolatileHistory
from .post_processing.file_output_post_processing import FileOutputPostProcessing
from .post_processing.ipost_processing import IPostProcessing
from .post_processing.no_post_processing import NoPostProcessing
from .post_processing.shell_execution_post_processing import ShellExecutionPostProcessing
from .processing.default_processing import DefaultProcessing
from .processing.file_processing import FileProcessing
from .processing.iprocessing import IProcessing
from .renderer.formatted_renderer import FormattedRenderer
from .renderer.irenderer import IRenderer
from .renderer.plain_renderer import PlainRenderer
from .session.chat_session_manager import ChatSessionManager
from .util import get_stdin, has_stdin, install_shell_integration, is_tty, print_version_callback

if TYPE_CHECKING:  # pragma: no cover
    from .configuration.schema import Role


class Application:
    def __init__(  # noqa: PLR0913, PLR0917
        self,
        prompt: Annotated[
            str,
            typer.Argument(show_default=False, help="Enter the prompt for generating completions."),
        ] = "",
        # input options
        editor: Annotated[
            bool,
            typer.Option(
                "--editor",
                "-e",
                help="Open the default text editor to provide a prompt.",
                rich_help_panel="Input Options",
            ),
        ] = False,
        repl: Annotated[
            bool,
            typer.Option(
                "--repl",
                "-r",
                help="Initiate a REPL (Read-eval-print loop) session.",
                rich_help_panel="Input Options",
            ),
        ] = False,
        files: Annotated[
            list[Path],
            typer.Option(
                "--file",
                "-f",
                exists=True,
                file_okay=True,
                dir_okay=False,
                writable=False,
                readable=True,
                resolve_path=True,
                help="Use one or more files as additional input.",
                rich_help_panel="Input Options",
            ),
        ] = [],  # noqa: B006
        # model options
        api: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(show_default=False, help="Select the API to be used.", rich_help_panel="Model Options"),
        ] = None,
        model: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(
                show_default=False,
                help="Choose the large language model to be utilized.",
                rich_help_panel="Model Options",
            ),
        ] = None,
        temperature: Annotated[
            Optional[float],  # noqa: FA100
            typer.Option(
                min=0.0,
                max=2.0,
                show_default=False,
                help="Adjust the randomness of the generated output.",
                rich_help_panel="Model Options",
            ),
        ] = None,
        top_probability: Annotated[
            Optional[float],  # noqa: FA100
            typer.Option(
                min=0.0,
                max=1.0,
                show_default=False,
                help="Limit the highest probable tokens (words).",
                rich_help_panel="Model Options",
            ),
        ] = None,
        # output options
        stream: Annotated[
            Optional[bool],  # noqa: FA100
            typer.Option(
                "--stream/--no-stream",
                help="Enable or disable stream output.",
                rich_help_panel="Output Options",
                show_default=False,
            ),
        ] = None,
        formatted: Annotated[
            Optional[bool],  # noqa: FA100
            typer.Option(
                "--formatted/--no-formatted",
                help="Enable or disable formatted output.",
                rich_help_panel="Output Options",
                show_default=False,
            ),
        ] = None,
        color: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(
                help="Set the output color.",
                rich_help_panel="Output Options",
                show_default=False,
            ),
        ] = None,
        theme: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(
                help="Choose the output theme.",
                rich_help_panel="Output Options",
                show_default=False,
            ),
        ] = None,
        output_file: Annotated[
            Optional[Path],  # noqa: FA100
            typer.Option(
                "--output",
                "-o",
                show_default=False,
                help="Specify a file to store the assistant's last message.",
                rich_help_panel="Output Options",
            ),
        ] = None,
        # cache options
        cache: Annotated[
            Optional[bool],  # noqa: FA100
            typer.Option(
                show_default=False,
                help="Enable or disable caching of completion results.",
                rich_help_panel="Cache Options",
            ),
        ] = None,
        _clear_cache: Annotated[
            bool,
            typer.Option(
                "--clear-cache",
                help="Clear the cache.",
                callback=Cache.clear_cache_callback,
                rich_help_panel="Cache Options",
            ),
        ] = False,
        # chat options
        chat_id: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(
                "--id",
                "-i",
                show_default=False,
                help="Start or continue a conversation with a specific chat ID.",
                rich_help_panel="Chat Options",
            ),
        ] = None,
        _show_chat: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(
                "--show-chat",
                show_default=False,
                help="Display all messages from the provided chat ID.",
                callback=ChatSessionManager.show_chat_callback,
                rich_help_panel="Chat Options",
            ),
        ] = None,
        _delete_chat: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(
                "--delete-chat",
                show_default=False,
                help="Delete a single chat with the specified ID.",
                callback=ChatSessionManager.delete_chat_callback,
                rich_help_panel="Chat Options",
            ),
        ] = None,
        _list_chats: Annotated[
            bool,
            typer.Option(
                "--list-chats",
                help="List all existing chat IDs.",
                callback=ChatSessionManager.list_chats_callback,
                rich_help_panel="Chat Options",
            ),
        ] = False,
        _clear_chats: Annotated[
            bool,
            typer.Option(
                "--clear-chats",
                show_default=False,
                help="Delete all chats.",
                callback=ChatSessionManager.clear_chats_callback,
                rich_help_panel="Chat Options",
            ),
        ] = False,
        # role options
        code: Annotated[
            bool,
            typer.Option("--code", "-c", help="Generate code only.", rich_help_panel="Role Options"),
        ] = False,
        describe_shell: Annotated[
            bool,
            typer.Option("--describe-shell", "-d", help="Describe a shell command.", rich_help_panel="Role Options"),
        ] = False,
        shell: Annotated[
            bool,
            typer.Option("--shell", "-s", help="Generate and execute shell commands.", rich_help_panel="Role Options"),
        ] = False,
        role: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(
                "--role",
                show_default=False,
                help="Define the system role for the large language model.",
                rich_help_panel="Role Options",
            ),
        ] = None,
        # other options
        _install_integration: Annotated[
            bool,
            typer.Option(
                "--install-integration",
                help="Install shell integration (Fish, Bash, ZSH and Powershell supported).",
                callback=install_shell_integration,
                rich_help_panel="Other Options",
            ),
        ] = False,
        _version: Annotated[
            bool,
            typer.Option(
                "--version",
                help="Display the current version.",
                callback=print_version_callback,
                rich_help_panel="Other Options",
            ),
        ] = False,
    ) -> None:
        self._prompt = prompt

        self._editor = editor
        self._repl = repl
        self._files = files

        self._api = api
        self._model = model
        self._temperature = temperature
        self._top_probability = top_probability

        self._stream = stream
        self._formatted = formatted
        self._color = color
        self._theme = theme
        self._output_file = output_file

        self._cache = cache
        self._chat_id = chat_id

        self._code = code
        self._describe_shell = describe_shell
        self._shell = shell
        self._role_name = role

        with ErrorHandler():
            self._get_prompt()
            self._validate()
            self._select_role()
            self._handle_request()

    def _get_prompt(self) -> None:
        if has_stdin():
            self._prompt = f"{self._prompt}\n\n{get_stdin()}"

        if self._editor:
            self._prompt = click.edit(self._prompt) or ""

    def _validate(self) -> None:
        for file in self._files:
            if "text" not in identify.tags_from_path(str(file.resolve())):
                raise FileError(str(file), hint="Only plain text files are supported")

        if sum((bool(self._role_name), self._code, self._describe_shell, self._shell)) > 1:
            raise UsageError("Only one of --role, --code, --describe-shell, --shell options can be used at a time.")

        if self._repl and has_stdin():
            raise UsageError("--repl can not be used with stdin")

        if self._shell and self._output_file:
            raise UsageError("Only one of --shell, --output-file options can be used at a time.")

        if not self._prompt:
            # repl is default mode if there is no other input
            self._repl = True

    def _select_role(self) -> None:
        self._role_name = self._role_name or cfg().config.default.role

        self._role: Role
        if self._code:
            self._role = cfg().config.builtin_roles.code
        elif self._describe_shell:
            self._role = cfg().config.builtin_roles.describe_shell
        elif self._shell:
            self._role = cfg().config.builtin_roles.shell
        elif self._role_name:
            if role := cfg().get_role(self._role_name):
                self._role = role
            else:
                raise ClickException(f"No such role: {self._role_name}")
        else:
            self._role = cfg().get_builtin_role_default()

        # override with cmd parameter
        self._override_role_options_from_cmd()

    def _handle_request(self) -> None:
        history = self._get_history()
        client = self._get_client()
        post_processing = self._get_post_processing(client)
        processing = self._get_processing(history, post_processing)
        renderer = self._get_renderer()
        handler = self._get_handler(client, processing, renderer)

        cache = self._cache if self._cache is not None else cfg().config.misc.session.cache

        try:
            handler.handle(
                self._prompt,
                model=self._role.options.model,
                temperature=self._role.options.temperature,
                top_probability=self._role.options.top_probability,
                stream=self._role.output.stream,
                caching=cache,
            )
        except errors.ApiError as e:
            raise ClickException(f"API error: {e}") from e
        except errors.RequestTimeoutError as e:
            raise ClickException("API request timed out") from e

    def _get_history(self) -> IHistory:
        if self._chat_id:
            session_manager = ChatSessionManager(
                cfg().config.misc.session.chat_history_path,
                cfg().config.misc.session.chat_history_size,
            )
            return PersistentHistory(self._chat_id, session_manager)
        else:
            return VolatileHistory()

    def _get_post_processing(self, client: IClient) -> IPostProcessing:
        if self._shell:
            return ShellExecutionPostProcessing(
                cfg().config.builtin_roles.shell,
                cfg().config.builtin_roles.describe_shell,
                client,
            )
        elif self._output_file:
            return FileOutputPostProcessing(self._output_file)
        else:
            return NoPostProcessing()

    def _get_processing(self, history: IHistory, post_processing: IPostProcessing) -> IProcessing:
        if self._files:
            return FileProcessing(self._role, self._files, history, post_processing)
        else:
            return DefaultProcessing(self._role, history, post_processing)

    def _get_renderer(self) -> IRenderer:
        if self._role.output.formatted and is_tty():
            return FormattedRenderer(self._role)
        else:
            return PlainRenderer(self._role)

    def _get_client(self) -> IClient:
        api = self._role.options.api
        if api == "chatgpt":
            if api_key := cfg().config.apis.chatgpt.api_key:
                return ChatGptClient(
                    api_key,
                    cfg().config.misc.request_timeout,
                    cfg().config.apis.chatgpt.azure_endpoint,
                )
            else:
                raise ClickException(f"No OpenAI API key, check {cfg().config_file()}")
        else:
            raise ClickException(f"Unknown API: {api}")

    def _get_handler(self, client: IClient, processing: IProcessing, renderer: IRenderer) -> IHandler:
        if self._repl:
            return ReplHandler(client, processing, renderer)
        else:
            return DefaultHandler(client, processing, renderer)

    def _override_role_options_from_cmd(self) -> None:
        options_to_override = [
            ("api", self._api),
            ("model", self._model),
            ("temperature", self._temperature),
            ("top_probability", self._top_probability),
        ]

        output_to_override = [
            ("stream", self._stream),
            ("formatted", self._formatted),
            ("color", self._color),
            ("theme", self._theme),
        ]

        try:
            for option, value in options_to_override:
                if value is not None:
                    setattr(self._role.options, option, value)

            for option, value in output_to_override:
                if value is not None:
                    setattr(self._role.output, option, value)
        except ValidationError as e:
            raise InvalidConfigError(e) from None


def run() -> None:
    typer.run(Application)
