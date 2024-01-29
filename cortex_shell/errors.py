from click import UsageError
from pydantic import ValidationError


class FatalError(RuntimeError):
    pass


class InvalidConfigError(UsageError):
    def __init__(self, validation_error: ValidationError) -> None:
        errors = validation_error.errors()
        output = [f"{len(errors)} errors in configuration"]
        for error in errors:
            location = ".".join(map(str, error["loc"]))
            output.append(f"{location}: {error['msg']}")
        super().__init__(message="\n".join(output))


class AuthenticationError(FatalError):
    pass


class RequestTimeoutError(FatalError):
    pass


class DeploymentNotFoundError(FatalError):
    pass


class ConnectError(FatalError):
    pass
