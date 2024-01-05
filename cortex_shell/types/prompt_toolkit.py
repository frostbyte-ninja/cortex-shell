from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from prompt_toolkit.formatted_text import (
    AnyFormattedText,
    StyleAndTextTuples,
    to_formatted_text,
)
from prompt_toolkit.formatted_text.utils import fragment_list_to_text
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import (
    Container,
    Window,
)
from prompt_toolkit.layout.controls import (
    FormattedTextControl,
)

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence

    from prompt_toolkit.key_binding.key_processor import KeyPressEvent

_T = TypeVar("_T")


class RadioListHorizontal(Generic[_T]):
    open_character = "("
    close_character = ")"
    container_style = "class:radio-list"
    default_style = "class:radio"
    selected_style = "class:radio-selected"
    checked_style = "class:radio-checked"

    def __init__(  # noqa: C901
        self,
        values: Sequence[tuple[_T, AnyFormattedText]],
        default_value: _T | None = None,
    ) -> None:
        assert len(values) > 0

        self.values = values

        keys: list[_T] = [value for (value, _) in values]
        self.current_value: _T = default_value if default_value in keys else values[0][0]

        self._selected_index = keys.index(self.current_value)

        bindings = KeyBindings()

        @bindings.add("left")  # type: ignore[misc]
        def _left(_event: KeyPressEvent) -> None:
            self._selected_index = max(0, self._selected_index - 1)

        @bindings.add("right")  # type: ignore[misc]
        def _right(_event: KeyPressEvent) -> None:
            self._selected_index = min(len(self.values) - 1, self._selected_index + 1)

        @bindings.add("pagedown")  # type: ignore[misc]
        def _pageup(event: KeyPressEvent) -> None:
            w = event.app.layout.current_window
            if w.render_info:
                self._selected_index = max(0, self._selected_index - len(w.render_info.displayed_lines))

        @bindings.add("pageup")  # type: ignore[misc]
        def _pagedown(event: KeyPressEvent) -> None:
            w = event.app.layout.current_window
            if w.render_info:
                self._selected_index = min(
                    len(self.values) - 1,
                    self._selected_index + len(w.render_info.displayed_lines),
                )

        @bindings.add(" ")  # type: ignore[misc]
        def _space(_event: KeyPressEvent) -> None:
            self._handle_space()

        @bindings.add("enter")  # type: ignore[misc]
        def _enter(event: KeyPressEvent) -> None:
            self._handle_space()
            event.app.exit(result=self.current_value)

        @bindings.add(Keys.Any)  # type: ignore[misc]
        def _find(event: KeyPressEvent) -> None:
            # We first check values after the selected value, then all values.
            values = list(self.values)
            for value in values[self._selected_index + 1 :] + values:
                text = fragment_list_to_text(to_formatted_text(value[1])).lower()

                if text.startswith(event.data.lower()):
                    self._selected_index = self.values.index(value)
                    return

        self.control = FormattedTextControl(self._get_text_fragments, key_bindings=bindings, focusable=True)

        self.window = Window(
            content=self.control,
            style=self.container_style,
            dont_extend_height=True,
        )

    def _handle_space(self) -> None:
        self.current_value = self.values[self._selected_index][0]

    def _get_text_fragments(self) -> StyleAndTextTuples:
        result: StyleAndTextTuples = []
        for i, value in enumerate(self.values):
            checked = value[0] == self.current_value
            selected = i == self._selected_index

            style = ""
            if checked:
                style += " " + self.checked_style
            if selected:
                style += " " + self.selected_style

            result.append((style, self.open_character))

            if selected:
                result.append(("[SetCursorPosition]", ""))

            if checked:
                result.append((style, "*"))
            else:
                result.append((style, " "))

            result.append((style, self.close_character))
            result.append((self.default_style, " "))
            result.extend(to_formatted_text(value[1], style=self.default_style))
            result.append(("", " "))

        for i in range(len(result)):
            result[i] = (result[i][0], result[i][1])

        return result

    def __pt_container__(self) -> Container:  # noqa: PLW3201
        return self.window
