# ===============================================================================
# Created:        20 Oct 2021
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Class to contain Anaplan Auth Token details required for all API calls
# Input:          Auth token value and expiry
# Output:         None
# ===============================================================================
from dataclasses import dataclass


@dataclass
class AuthToken(object):
    """
    AuthToken object stores Anaplan auth header and expiry time
    :param token_value: AnaplanAuthToken value
    :type token_value: str
    :param token_expiry: Expiry time in epoch
    :type token_expiry: float
    """
    token_value: str
    token_expiry: float

    def __init__(self, token_value: str, token_expiry: float):
        """
        :param token_value: Hexadecimal API authorization string
        :type token_value: str
        :param token_expiry: Expiry time of auth token in epoch
        :type token_expiry: float
        """
        self.token_value = AuthToken._token_convert(token_value)
        self.token_expiry = token_expiry

    def get_auth_token(self) -> str:
        """Get auth token value

        :return: Auth token value
        :rtype: str
        """
        return self.token_value

    def set_auth_token(self, token_value: str):
        """Update auth token value

        :param token_value: New token value to set
        :type token_value: str
        """
        self.token_value = token_value

    def get_token_expiry(self) -> float:
        """Get token expiry value

        :return: Token expiry time
        :rtype: float
        """
        return self.token_expiry

    def set_token_expiry(self, token_expiry):
        """Update token expiry time

        :param token_expiry: New expiry time of auth token in epoch
        :type token_expiry: float
        """
        self.token_expiry = token_expiry

    @staticmethod
    def _token_convert(token_value: str) -> str:
        """Ensures provided token value matches expected format

        :param token_value: Auth token value
        :type token_value: str
        :return: Auth token value formatted for request headers
        :rtype: str
        """
        if not token_value[:7] == "Anaplan":
            return ''.join(['AnaplanAuthToken ', token_value])
        else:
            return token_value
