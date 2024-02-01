from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, ConfigDict, Field
from pydantic import BaseModel as PydanticBaseModel
from typing_extensions import Self

from .. import constants as C  # noqa: N812
from ..role import CODE_ROLE, DESCRIBE_SHELL_ROLE, SHELL_ROLE
from ..util import fill_values, get_temp_dir
from .validator import (
    check_api,
    check_color,
    check_path,
    check_role_name,
    check_url,
    description_validator,
)

PathType = Annotated[Path, BeforeValidator(check_path)]
ApiType = Annotated[str, AfterValidator(check_api)]
ColorType = Annotated[str, AfterValidator(check_color)]
UrlType = Annotated[str, AfterValidator(check_url)]
TemperatureType = Annotated[float, Field(ge=0.0, le=2.0)]
TopProbabilityType = Annotated[float, Field(ge=0.0, le=1.0)]
BuiltinRoleNameType = Annotated[str, AfterValidator(check_role_name), Field(exclude=True)]
DescriptionType = Annotated[
    str,
    AfterValidator(description_validator),
    Field(validate_default=True),
]
BuiltinDescriptionType = Annotated[
    str,
    AfterValidator(description_validator),
    Field(exclude=True, validate_default=True),
]


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(validate_assignment=True, strict=True)


class ChatGPT(BaseModel):
    api_key: str | None = None
    azure_endpoint: UrlType | None = None
    azure_deployment: str | None = None


class APIs(BaseModel):
    chatgpt: ChatGPT = ChatGPT()


class Session(BaseModel):
    chat_history_path: PathType = Field((Path.home() / ".cache" / C.PROJECT_NAME / "history").resolve())
    chat_history_size: int = Field(100, gt=0)
    chat_cache_path: PathType = Field((get_temp_dir() / C.PROJECT_NAME / "cache").resolve())
    chat_cache_size: int = Field(100, gt=0)
    cache: bool = True


class Misc(BaseModel):
    request_timeout: int = Field(10, ge=0)
    session: Session = Session()


class Options(BaseModel):
    api: ApiType = "chatgpt"
    model: str = "gpt-4-1106-preview"
    temperature: TemperatureType = 0.1
    top_probability: TopProbabilityType = 1.0


class Output(BaseModel):
    stream: bool = True
    formatted: bool = True
    color: ColorType = "blue"
    theme: str = "dracula"


class Default(BaseModel):
    role: str | None = None
    options: Options = Options()
    output: Output = Output()


class Role(BaseModel):
    name: str
    description: DescriptionType
    options: Options | None = None
    output: Output | None = Field(None, exclude=True)


class BuiltinRoleCode(Role):
    name: BuiltinRoleNameType = "code"
    description: BuiltinDescriptionType = CODE_ROLE


class BuiltinRoleShell(Role):
    name: BuiltinRoleNameType = "shell"
    description: BuiltinDescriptionType = SHELL_ROLE
    default_execute: bool = False


class BuiltinRoleDescribeShell(Role):
    name: BuiltinRoleNameType = "describe_shell"
    description: BuiltinDescriptionType = DESCRIBE_SHELL_ROLE


class BuiltinRoles(BaseModel):
    code: BuiltinRoleCode = BuiltinRoleCode()
    shell: BuiltinRoleShell = BuiltinRoleShell()
    describe_shell: BuiltinRoleDescribeShell = BuiltinRoleDescribeShell()


class Configuration(BaseModel):
    apis: APIs = APIs()
    misc: Misc = Misc()
    default: Default = Default()
    builtin_roles: BuiltinRoles = BuiltinRoles()
    roles: list[Role] | None = None

    def populate_roles(self) -> Self:
        # Fill empty values in roles with values from the default section
        for role in list(self.builtin_roles.__dict__.values()) + (self.roles or []):
            fill_values(
                Role(name="", description="", options=self.default.options, output=self.default.output),
                role,
            )

        self.builtin_roles.shell.output.formatted = False
        self.builtin_roles.code.output.formatted = False

        return self
