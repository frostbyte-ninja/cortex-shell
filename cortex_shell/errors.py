class FatalError(RuntimeError):
    pass


class InvalidConfigError(FatalError):
    pass


class AuthenticationError(FatalError):
    pass
