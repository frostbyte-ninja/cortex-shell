from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, cast

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout

from ..handlers.default_handler import DefaultHandler
from ..processing.default_processing import DefaultProcessing
from ..renderer.formatted_renderer import FormattedRenderer
from ..renderer.plain_renderer import PlainRenderer
from ..types.prompt_toolkit import RadioListHorizontal
from ..util import get_colored_text, has_stdin, is_tty, run_command
from .ipost_processing import IPostProcessing

if TYPE_CHECKING:  # pragma: no cover
    from ..client.iclient import IClient
    from ..configuration.schema import BuiltinRoleDescribeShell, BuiltinRoleShell
    from ..handlers.ihandler import IHandler
    from ..renderer.irenderer import IRenderer
    from ..types import Message


class Option(Enum):
    EXECUTE = 0
    DESCRIBE = 1
    ABORT = 2


class ShellExecutionPostProcessing(IPostProcessing):
    def __init__(self, shell_role: BuiltinRoleShell, describe_shell_role: BuiltinRoleDescribeShell, client: IClient):
        self._shell_role = shell_role
        self._describe_shell_role = describe_shell_role
        self._handler = self._get_shell_describe_handler(client)

    def __call__(self, messages: list[Message]) -> None:
        if has_stdin() or not is_tty():
            # do nothing if we are reading from a pipe or redirecting output
            return

        current_assistant_message = messages[-1]["content"]
        while True:
            option = self._prompt()
            if option == Option.EXECUTE:
                run_command(current_assistant_message)
                break
            elif option == Option.DESCRIBE:
                self._handler.handle(
                    current_assistant_message,
                    model=self._describe_shell_role.options.model,
                    temperature=self._describe_shell_role.options.temperature,
                    top_probability=self._describe_shell_role.options.top_probability,
                    stream=self._describe_shell_role.output.stream,
                    caching=False,
                )
            elif option == Option.ABORT:
                break

    def _prompt(self) -> Option:
        default_option = Option.EXECUTE if self._shell_role.default_execute else Option.ABORT
        options = RadioListHorizontal(
            [
                (Option.EXECUTE, get_colored_text("[e]xecute", "green")),
                (Option.DESCRIBE, get_colored_text("[d]escribe", "yellow")),
                (Option.ABORT, get_colored_text("[a]bort", "red")),
            ],
            default_option,
        )
        bindings = KeyBindings()

        @bindings.add("e")  # type: ignore[misc]
        def _execute(event: KeyPressEvent) -> None:
            options.current_value = Option.EXECUTE
            event.app.exit(result=options.current_value)

        @bindings.add("d")  # type: ignore[misc]
        def _describe(event: KeyPressEvent) -> None:
            options.current_value = Option.DESCRIBE
            event.app.exit(result=options.current_value)

        @bindings.add("a")  # type: ignore[misc]
        def _abort(event: KeyPressEvent) -> None:
            options.current_value = Option.ABORT
            event.app.exit(result=options.current_value)

        @bindings.add(Keys.ControlC)  # type: ignore[misc]
        def _control_c(_event: KeyPressEvent) -> None:
            raise KeyboardInterrupt

        return cast(Option, Application[Option](layout=Layout(options), key_bindings=bindings).run())

    def _get_shell_describe_handler(self, client: IClient) -> IHandler:
        renderer: IRenderer
        if self._describe_shell_role.output.formatted:
            renderer = FormattedRenderer(self._describe_shell_role)
        else:
            renderer = PlainRenderer(self._describe_shell_role)

        return DefaultHandler(
            client,
            DefaultProcessing(self._describe_shell_role),
            renderer,
        )
