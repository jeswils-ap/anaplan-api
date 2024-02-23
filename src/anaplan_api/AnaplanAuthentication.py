# ===============================================================================
# Created:			1 Nov 2021
# @author:			Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:		Abstract Anaplan Authentication Class
# Input:			Username & Password, or SHA keypair
# Output:			Anaplan JWT and token expiry time
# ===============================================================================
import json
import re
import logging
from .AuthToken import AuthToken
from .util.Util import AuthenticationFailedError
from .util.RequestHandler import RequestHandler

logger = logging.getLogger(__name__)


class AnaplanAuthentication(object):
    """
    Represents an authentication attempt for Anaplan API
    """

    def __init__(self, request_handler: RequestHandler, **kwargs):
        self.handler = request_handler

    def auth_header(self, username: str, password: str):
        pass

    def auth_request(self, header: dict, body: str = None) -> dict:
        """Sends authentication request to Anaplan auth server

        :param header: Authorization header for request to auth server
        :type header: dict
        :param body: JSON body of auth request
        :type body: str
        :return: JSON string with auth token details
        :rtype: dict
        """
        anaplan_url = "https://auth.anaplan.com/token/authenticate"

        if body is None:
            logger.info("Authenticating via Basic.")
            try:
                authenticate = self.handler.make_request(
                    "", "POST", headers=header, override_url=anaplan_url
                ).json()
            except Exception as e:
                logger.error(f"Error fetching auth token {e}", exc_info=True)
                raise Exception(f"Error fetching auth token {e}")
        else:
            logger.info("Authenticating via Certificate.")
            try:
                authenticate = self.handler.make_request(
                    "",
                    "POST",
                    headers=header,
                    data=json.dumps(body),
                    override_url=anaplan_url,
                ).json()
            except Exception as e:
                logger.error(f"Error fetching auth token {e}", exc_info=True)
                raise Exception(f"Error fetching auth token {e}")

        # Return the JSON array containing the authentication response, including AnaplanAuthToken
        return authenticate

    def authenticate(self, response: dict) -> AuthToken:
        """Parses the authentication response

        :param response: JSON string with auth request response.
        :type response: str
        :return: AnaplanAuthToken and expiry in epoch
        :rtype: AuthToken
        """
        if "status" not in response:
            logger.error(
                "Error occurred processing response. Does not appear well formed"
            )
            logger.error(f"Response contents:\n{response}")
            raise AuthenticationFailedError(
                "Error occurred processing response. Does not appear well formed"
            )

        if not isinstance(response["status"], str):
            logger.error(f"Unexpected status: {response['status']}")
            raise AuthenticationFailedError(f"Unexpected status: {response['status']}")

        err_regex = re.compile("FAILURE.+")
        if bool(re.match(err_regex, response["status"])):
            logger.error(f"Error {response['statusMessage']}")
            raise AuthenticationFailedError(
                f"Error logging in {response['statusMessage']}"
            )

        token = response["tokenInfo"]["tokenValue"]
        expires = response["tokenInfo"]["expiresAt"]
        status = self.verify_auth(token)

        if status != "Token validated":
            logger.error(f"Error {status}")
            raise AuthenticationFailedError(f"Error getting authentication {status}")

        logger.info("User successfully authenticated.")
        return AuthToken(f"AnaplanAuthToken {token}", expires)

    def verify_auth(self, token: str) -> str:
        """Verifies the authentication request

        :param token: AnaplanAuthToken from authentication request.
        :type token: str
        :return: JSON string with authentication validation.
        :rtype: str
        """

        anaplan_url = "https://auth.anaplan.com/token/validate"
        header = {"Authorization": "".join(["AnaplanAuthToken ", token])}

        try:
            logger.debug("Verifying auth token.")
            validate = self.handler.make_request(
                "", "GET", headers=header, override_url=anaplan_url
            ).json()
        except Exception as e:
            logger.error(f"Error verifying auth token {e}", exc_info=True)
            raise Exception(f"Error verifying auth token {e}")

        if "statusMessage" not in validate:
            logger.error("Unable to find authentication status.")
            raise ValueError("Unable to find authentication status.")

        return validate["statusMessage"]

    def refresh_token(self, token: str, auth_object: AuthToken):
        """Refreshes the authentication token and updates the token expiry time

        :param token: Token value that is nearing expiry
        :type token: str
        :param auth_object: AuthToken object to be updated.
        :type auth_object: AuthToken
        """
        new_token = ""
        new_expiry = ""

        url = "https://auth.anaplan.com/token/refresh"
        header = {"Authorization": "".join(["AnaplanAuthToken ", token])}
        try:
            refresh = self.handler.make_request(
                "", "POST", headers=header, override_url=url
            ).json()
        except Exception as e:
            logger.error(f"Error verifying auth token {e}", exc_info=True)
            raise Exception(f"Error verifying auth token {e}")

        if "tokenInfo" in refresh:
            if "tokenValue" in refresh["tokenInfo"]:
                new_token = refresh["tokenInfo"]["tokenValue"]
            if "expiresAt" in refresh["tokenInfo"]:
                new_expiry = refresh["tokenInfo"]["expiresAt"]

        auth_object.token_value = "".join(["AnaplanAuthToken ", new_token])
        auth_object.token_expiry = new_expiry
