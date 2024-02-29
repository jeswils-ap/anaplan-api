# ===============================================================================
# Created:        20 Oct 2021
# @author:        Jesse Wilson
# Description:    Class to contain Anaplan Auth Token details required for all API calls
# Input:          Auth token value and expiry
# Output:         None
# ===============================================================================
import threading
from dataclasses import dataclass
from AnaplanAuthentication import AnaplanAuthentication


@dataclass
class AuthToken(object):
    """
    AuthToken object stores Anaplan auth header and expiry time
    :param _token_value: AnaplanAuthToken value
    :type _token_value: str
    :param _token_expiry: Expiry time in epoch
    :type _token_expiry: float
    :param _refresh_timeout: Amount of time (in seconds) the AuthToken value is valid
    :type _refresh_timeout: int
    """

    _token_value: str
    _token_expiry: float
    _refresh_timeout: int = 60 * 60 * 29  # Refresh token after 29 minutes

    def __init__(self, token_value: str, token_expiry: float):
        self._token_value = token_value
        self._token_expiry = token_expiry
        self.authorizer = AnaplanAuthentication()
        self.timer = None
        self.delay = self._refresh_timeout
        self.start()

    def __post_init__(self):
        if not self._token_value[:7] == "Anaplan":
            self._token_value = "".join(["AnaplanAuthToken ", self._token_value])

    def _run(self):
        self.start()
        self._token_value, self._token_expiry = self.authorizer.refresh_token(self.token_value)

    def start(self):
        self.timer = threading.Timer(self.delay, self._run)
        self.timer.daemon = True
        self.timer.name = "authorization_refresh"
        self.timer.start()

    def cancel(self):
        if self.timer:
            self.timer.cancel()

    @property
    def token_value(self) -> str:
        """Get auth token value

        :return: Auth token value
        :rtype: str
        """
        return self._token_value

    @token_value.setter
    def token_value(self, new_token_value: str) -> None:
        """Update auth token value

        :param new_token_value: New token value to set
        :type new_token_value: str
        """
        self.token_value = new_token_value

    @property
    def token_expiry(self) -> float:
        """Get token expiry value

        :return: Token expiry time
        :rtype: float
        """
        return self.token_expiry

    @token_expiry.setter
    def token_expiry(self, token_expiry: float) -> None:
        """Update token expiry time

        :param token_expiry: New expiry time of auth token in epoch
        :type token_expiry: float
        """
        self.token_expiry = token_expiry
