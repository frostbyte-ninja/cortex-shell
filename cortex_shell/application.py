from pathlib import Path
from typing import Annotated, Optional, cast

import click
import typer
from click import UsageError

from .cache import Cache
from .chat_session import ChatSession
from .client.chatgpt_client import ChatGptClient
from .client.iclient import IClient
from .configuration import cfg
from .error_handler import ErrorHandler
from .errors import AuthenticationError
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
from .role import ShellRole
from .util import get_stdin, has_stdin, install_shell_integration, is_tty, print_version_callback

# mypy: disable-error-code="union-attr"


class Application:
    def __init__(  # noqa: PLR0913, PLR0917
        self,
        prompt: Annotated[str, typer.Argument(show_default=False, help="The prompt to generate completions for.")] = "",
        # input options
        editor: Annotated[
            bool,
            typer.Option("--editor", "-e", help="Open $EDITOR to provide a prompt.", rich_help_panel="Input Options"),
        ] = False,
        repl: Annotated[
            bool,
            typer.Option(
                "--repl",
                "-r",
                help="Start a REPL (Read-eval-print loop) session.",
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
                help="Use one or multiple files as additional input.",
                rich_help_panel="Input Options",
            ),
        ] = [],  # noqa: B006
        # model options
        api: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(show_default=False, help="API to use.", rich_help_panel="Model Options"),
        ] = None,
        model: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(show_default=False, help="Large language model to use.", rich_help_panel="Model Options"),
        ] = None,
        temperature: Annotated[
            Optional[float],  # noqa: FA100
            typer.Option(
                min=0.0,
                max=2.0,
                show_default=False,
                help="Randomness of generated output.",
                rich_help_panel="Model Options",
            ),
        ] = None,
        top_probability: Annotated[
            Optional[float],  # noqa: FA100
            typer.Option(
                min=0.0,
                max=1.0,
                show_default=False,
                help="Limits highest probable tokens (words).",
                rich_help_panel="Model Options",
            ),
        ] = None,
        # output options
        stream: Annotated[
            Optional[bool],  # noqa: FA100
            typer.Option(
                "--stream/--no-stream",
                help="Enable stream output.",
                rich_help_panel="Output Options",
                show_default=False,
            ),
        ] = None,
        formatted: Annotated[
            Optional[bool],  # noqa: FA100
            typer.Option(
                "--formatted/--no-formatted",
                help="Enable formatted output.",
                rich_help_panel="Output Options",
                show_default=False,
            ),
        ] = None,
        color: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(
                help="Output color.",
                rich_help_panel="Output Options",
                show_default=False,
            ),
        ] = None,
        theme: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(
                help="Output theme.",
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
                help="A file where the last message from the assistant will be stored.",
                rich_help_panel="Output Options",
            ),
        ] = None,
        # cache options
        cache: Annotated[
            Optional[bool],  # noqa: FA100
            typer.Option(show_default=False, help="Cache completion results.", rich_help_panel="Cache Options"),
        ] = None,
        _clear_cache: Annotated[
            bool,
            typer.Option(
                "--clear-cache",
                help="Clear cache.",
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
                help="Follow conversation with an id.",
                rich_help_panel="Chat Options",
            ),
        ] = None,
        _show_chat: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(
                "--show-chat",
                show_default=False,
                help="Show all messages from a provided chat id.",
                callback=ChatSession.show_messages_callback,
                rich_help_panel="Chat Options",
            ),
        ] = None,
        _delete_chat: Annotated[
            Optional[str],  # noqa: FA100
            typer.Option(
                "--delete-chat",
                show_default=False,
                help="Delete a single chat with id.",
                callback=ChatSession.delete_messages_callback,
                rich_help_panel="Chat Options",
            ),
        ] = None,
        _list_chats: Annotated[
            bool,
            typer.Option(
                "--list-chats",
                help="List all existing chat ids.",
                callback=ChatSession.list_ids_callback,
                rich_help_panel="Chat Options",
            ),
        ] = False,
        _clear_chats: Annotated[
            bool,
            typer.Option(
                "--clear-chats",
                show_default=False,
                help="Clear all chats.",
                callback=ChatSession.clear_chats_callback,
                rich_help_panel="Chat Options",
            ),
        ] = False,
        # role options
        code: Annotated[
            bool,
            typer.Option("--code", "-c", help="Generate only code.", rich_help_panel="Role Options"),
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
                help="System role for GPT model.",
                rich_help_panel="Role Options",
            ),
        ] = None,
        # other options
        _install_integration: Annotated[
            bool,
            typer.Option(
                "--install-integration",
                help="Install shell integration (Fish, Bash and ZSH supported).",
                callback=install_shell_integration,
                rich_help_panel="Other Options",
            ),
        ] = False,
        _version: Annotated[
            bool,
            typer.Option(
                "--version",
                help="Show version.",
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
        self._role_name = self._role_name or cfg().default_role()

        if self._code:
            self._role = cfg().get_builtin_role_code()
        elif self._describe_shell:
            self._role = cfg().get_builtin_role_describe_shell()
        elif self._shell:
            self._role = cfg().get_builtin_role_shell()
        elif self._role_name:
            if role := cfg().get_role(self._role_name):
                self._role = role
            else:
                raise UsageError(f"No such role: {self._role_name}")
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

        cache = self._cache if self._cache is not None else cfg().cache()

        try:
            handler.handle(
                self._prompt,
                model=self._role.options.model,
                temperature=self._role.options.temperature,
                top_probability=self._role.options.top_probability,
                stream=self._role.output.stream,
                caching=cache,
            )
        except AuthenticationError as ex:
            raise UsageError(f"Authentication Error: {ex}, check {cfg().config_file()}") from ex
        except ValueError as ex:
            raise UsageError(str(ex)) from ex

    def _get_history(self) -> IHistory:
        if self._chat_id:
            return PersistentHistory(self._chat_id, cfg().chat_history_size(), cfg().chat_history_path())
        else:
            return VolatileHistory()

    def _get_post_processing(self, client: IClient) -> IPostProcessing:
        if self._shell:
            return ShellExecutionPostProcessing(
                cast(ShellRole, self._role),
                cfg().get_builtin_role_describe_shell(),
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
        if self._role.output.formatted and is_tty() and not self._shell and not self._code:
            return FormattedRenderer(self._role)
        else:
            return PlainRenderer(self._role)

    def _get_client(self) -> IClient:
        api = self._role.options.api
        if api == "chatgpt":
            return ChatGptClient(
                cfg().chat_gpt_api_key(),  # type: ignore[arg-type]
                cfg().request_timeout(),
                cfg().azure_endpoint(),
                cfg().azure_deployment(),
            )
        else:
            raise UsageError(f"Unknown API: {api}")

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

        for option, value in options_to_override:
            if value is not None:
                setattr(self._role.options, option, value)

        for option, value in output_to_override:
            if value is not None:
                setattr(self._role.output, option, value)


def run() -> None:
    typer.run(Application)
