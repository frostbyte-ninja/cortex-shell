from __future__ import annotations

from typing import Any

from .util import os_name, shell_name

DEFAULT_ROLE = """You are a programming and system administration assistant.
You are managing {os} operating system with {shell} shell.
Provide short and concise answers, unless you are asked for further details.
Apply Markdown syntax to your answers when possible.
If you need to store any data, assume it will be stored in the conversation.
Do not display warnings or information about your capabilities."""

CODE_ROLE = """Provide only code as output.
Do not give any description or explanation about the code.
Offer the most logical solution if details are insufficient.
Keep the code in plain text format without any Markdown syntax like "```".
Do not ask for more details.
For example, if the prompt is "Hello world Python", return "print('Hello world')".
Do not display warnings or information about your capabilities."""

SHELL_ROLE = """Provide only commands for "{shell}" shell on "{os}" operating system without any description, prioritizing shell compatibility over the operating system.
Offer the most logical solution if details are insufficient.
If multiple steps are required try to combine them together using "&&".
Ensure the output is a valid shell command for the specified shell.
Keep the output in plain text format without any Markdown syntax like "```"."""

DESCRIBE_SHELL_ROLE = """Provide a concise description of the given shell command in a single sentence.
Describe every sub-command and every parameter of the provided command in a list.
Keep responses short.
Apply Markdown syntax to your answers when possible."""

FILE_ROLE = """Process and analyze files as input but do not provide any output about them.
Treat every input as a file until the next system prompt.
After processing, answer questions about these files.
Refer to input data when the user mentions files.
If you need to store any data, assume it will be stored in the conversation.
If no file is named directly by the user, refer to the most logical file."""


class Options:
    def __init__(
        self,
        api: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        top_probability: float | None = None,
    ):
        self.api = api
        self.model = model
        self.temperature = temperature
        self.top_probability = top_probability

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Options:
        return cls(**data)


class Output:
    def __init__(
        self,
        stream: bool | None = None,
        formatted: bool | None = None,
        color: str | None = None,
        theme: str | None = None,
    ):
        self.stream = stream
        self.formatted = formatted
        self.color = color
        self.theme = theme

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Output:
        return cls(**data)


class Role:
    def __init__(
        self,
        name: str,
        description: str,
        options: Options | None = None,
        output: Output | None = None,
    ):
        self.name = name
        self.description = description.format(shell=shell_name(), os=os_name())
        self.options = options or Options()
        self.output = output or Output()

    def fill_from(self, other: Role) -> None:
        for attr_name in ["options", "output"]:
            current_attr = getattr(self, attr_name)
            other_attr = getattr(other, attr_name)

            if current_attr is None:
                setattr(self, attr_name, other_attr)
            elif other_attr is not None:
                for sub_attr_name in vars(current_attr):
                    current_sub_attr = getattr(current_attr, sub_attr_name)
                    other_sub_attr = getattr(other_attr, sub_attr_name)

                    if current_sub_attr is None and other_sub_attr is not None:
                        setattr(current_attr, sub_attr_name, other_sub_attr)


class ShellRole(Role):
    def __init__(
        self,
        id: str,  # noqa: A002
        description: str,
        default_execute: bool,
        options: Options | None = None,
        output: Output | None = None,
    ):
        super().__init__(id, description, options, output)
        self.default_execute = default_execute
