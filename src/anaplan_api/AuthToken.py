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
    """AuthToken object stores Anaplan auth header and expiry time"""
    token_value: str
    token_expiry: float

    def __init__(self, token_value: str, token_expiry: float):
        self.token_value = AuthToken._token_convert(token_value)
        self.token_expiry = token_expiry

    def get_auth_token(self) -> str:
        return self.token_value

    def set_auth_token(self, token_value):
        self.token_value = token_value

    def get_token_expiry(self) -> float:
        return self.token_expiry

    def set_token_expiry(self, token_expiry):
        self.token_expiry = token_expiry

    @staticmethod
    def _token_convert(token_value: str) -> str:
        if not token_value[:7] == "Anaplan":
            return ''.join(['AnaplanAuthToken ', token_value])
        else:
            return token_value
