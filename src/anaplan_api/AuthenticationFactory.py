import logging
from .BasicAuthentication import BasicAuthentication
from .CertificateAuthentication import CertificateAuthentication

logger = logging.getLogger(__name__)


class AuthenticationFactory:
    _auth_classes = {
        "basic": BasicAuthentication,
        "certificate": CertificateAuthentication
    }

    @staticmethod
    def create_authentication(method, **kwargs):
        if method not in AuthenticationFactory._auth_classes:
            raise ValueError(f"Invalid authentication method: {method}. Should be one of {','.join(AuthenticationFactory._auth_classes.keys())}")

        auth_class = AuthenticationFactory._auth_classes[method]
        required_params = auth_class._required_params

        provided_params = set(kwargs.keys())
        missing_params = required_params - provided_params

        if missing_params:
            raise ValueError(f"Missing required parameters for {method} authentication: {missing_params}")

        return auth_class(**kwargs)
