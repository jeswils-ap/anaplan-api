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


class InvalidAuthenticationError(ValueError):
    pass


class MappingParameterError(ValueError):
    pass


class InvalidUrlError(ValueError):
    pass


class InvalidTaskTypeError(ValueError):
    pass


class InvalidKeyError(ValueError):
    pass


class InvalidKeyError(ValueError):
    pass
