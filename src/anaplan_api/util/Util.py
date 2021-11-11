class ResourceNotFoundError(KeyError):
    pass


class UnknownTaskTypeError(KeyError):
    pass


class TaskParameterError(KeyError):
    pass


class InvalidTokenError(AttributeError):
    pass


class RequestFailedError(ValueError):
    pass


class AuthenticationFailedError(Exception):
    pass
