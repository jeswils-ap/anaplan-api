# ==============================================================================
# Created:		28 June 2018
# @author:		Jesse Wilson  (Anaplan Asia Pte Ltd)
# Description:	This script reads a user's public and private keys in order to
# 				sign a cryptographic nonce. It then generates a request to
# 				authenticate with Anaplan, passing the signed and unsigned
# 				nonce in the body of the request.
# Input:		Public certificate file location, private key file location
# Output:		Authorization header string, request body string containing a nonce and its signed value
# ==============================================================================
import logging
from base64 import b64encode
from typing import Dict
from .AnaplanAuthentication import AnaplanAuthentication

logger = logging.getLogger(__name__)


class BasicAuthentication(AnaplanAuthentication):
    _required_params: set = {"email", "password"}

    """
    Represents a basic authentication header request
    """

    # ===========================================================================
    # This function takes in the Anaplan username and password, base64 encodes
    # them, then returns the basic authorization header.
    # ===========================================================================
    @staticmethod
    def auth_header(email: str, password: str, **kwargs) -> Dict[str, str]:
        """Takes an Anaplan username and password, encodes in base64 and creates an auth request header

        :param email: Anaplan username
        :type email: str
        :param password: Anaplan password
        :type password: str
        :return: Auth-API request authorization header
        :rtype: dict
        """

        logger.debug("Generating Authorization header")
        return {
            "Authorization": "".join(
                [
                    "Basic ",
                    b64encode((email + ":" + password).encode("utf-8")).decode(
                        "utf-8"
                    ),
                ]
            )
        }

    @property
    def required_params(self) -> set:
        return self._required_params
