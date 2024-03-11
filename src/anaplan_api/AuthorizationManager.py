# ===============================================================================
# Created:        11 Mar 2024
# @author:        Jesse Wilson
# Description:    This class manages spawning of authorisation-related classes.
# Input:          Authentication method and related arguments
# Output:         Self
# ===============================================================================
import logging
import threading
from .AnaplanAuthentication import AnaplanAuthentication
from .AuthenticationFactory import AuthenticationFactory
from src.anaplan_api.models.AuthToken import AuthToken

logger = logging.getLogger(__name__)


class AuthorizationManager:
    """
    AuthorizationManager is responsible for generating an Authentication class for the user
    to obtain a token from Anaplan. Upon success, it creates an AuthToken and manages token
    refresh for the user.
    :param _timer: Thread created to automatically refresh an AnaplanAuthToken before expiry
    :type _timer: threading.Timer
    :param _refresh_timeout: Amount of time (in seconds) the AuthToken value is valid
    :type _refresh_timeout: int
    :param _authorizer: Class to manager token refresh functions
    :type _authorizer: AnaplanAuthentication
    :param _auth_token: Dataclass containing the token value and expiry
    :type _auth_token: AuthToken
    """

    _timer: threading.Timer
    _refresh_timeout: int = 60 * 60 * 29  # Refresh token after 29 minutes
    _authorizer: AnaplanAuthentication
    _auth_token: AuthToken

    def __init__(self, method: str, **kwargs):
        self.authorizer = AnaplanAuthentication()
        self.timer = None
        self.create_auth(method.lower(), **kwargs)
        self.start()

    def create_auth(self, method: str, **kwargs):
        authenticator = AuthenticationFactory().create_authentication(method, **kwargs)
        header_string = authenticator.auth_header(**kwargs)
        post_data = None
        if method != "basic":
            post_data = authenticator.generate_post_data(**kwargs)
        token, expiry = authenticator.authenticate(
            authenticator.auth_request(header_string, post_data)
        )
        self._auth_token = AuthToken(token, expiry)

    @property
    def auth_token(self) -> AuthToken:
        return self._auth_token

    def _run(self):
        self.start()
        new_token_value, new_token_expiry = self.authorizer.refresh_token(
            self._auth_token.token_value
        )
        self._auth_token.token_value = new_token_value
        self._auth_token.token_expiry = new_token_expiry

    def start(self):
        self.timer = threading.Timer(self._refresh_timeout, self._run)
        self.timer.daemon = True
        self.timer.name = "authorization_refresh"
        self.timer.start()

    def cancel(self):
        if self.timer:
            self.timer.cancel()
