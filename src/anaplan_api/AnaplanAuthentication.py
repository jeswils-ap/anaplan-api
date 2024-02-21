# ===============================================================================
# Created:			1 Nov 2021
# @author:			Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:		Abstract Anaplan Authentication Class
# Input:			Username & Password, or SHA keypair
# Output:			Anaplan JWT and token expiry time
# ===============================================================================
import json
import requests
import re
import logging
from requests.exceptions import (
    HTTPError,
    ConnectionError,
    SSLError,
    Timeout,
    ConnectTimeout,
    ReadTimeout,
)
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

    def auth_request(self, header: dict, body: str = None) -> str:
        """Sends authentication request to Anaplan auth server

        :param header: Authorization header for request to auth server
        :type header: dict
        :param body: JSON body of auth request
        :type body: str
        :return: JSON string with auth token details
        :rtype: str
        """
        anaplan_url = "https://auth.anaplan.com/token/authenticate"

        if body is None:
            logger.info("Authenticating via Basic.")
            try:
                authenticate = self.handler.make_request(
                    anaplan_url, "POST", headers=header
                ).text
            except Exception as e:
                logger.error(f"Error fetching auth token {e}", exc_info=True)
                raise Exception(f"Error fetching auth token {e}")
        else:
            logger.info("Authenticating via Certificate.")
            try:
                authenticate = self.handler.make_request(
                    anaplan_url, "POST", headers=header, data=json.dumps(body)
                ).text
            except Exception as e:
                logger.error(f"Error fetching auth token {e}", exc_info=True)
                raise Exception(f"Error fetching auth token {e}")

        # Return the JSON array containing the authentication response, including AnaplanAuthToken
        return authenticate

    @staticmethod
    def authenticate(response: str) -> AuthToken:
        """Parses the authentication response

        :param response: JSON string with auth request response.
        :type response: str
        :return: AnaplanAuthToken and expiry in epoch
        :rtype: AuthToken
        """
        try:
            json_response = json.loads(response)
        except ValueError as e:
            logger.error(f"Error loading response JSON {e}", exc_info=True)
            raise ValueError(f"Error loading JSON {response}")

        # Check that the request was successful, is so extract the AnaplanAuthToken value
        if "status" not in json_response:
            logger.error(
                "Error occurred processing response. Does not appear well formed"
            )
            logger.error(f"Response contents:\n{json_response}")
            raise AuthenticationFailedError(
                "Error occurred processing response. Does not appear well formed"
            )

        if isinstance(json_response["status"], dict):
            logger.error(f"Unexpected status: {json_response['status']}")
            raise AuthenticationFailedError(
                f"Unexpected status: {json_response['status']}"
            )

        err_regex = re.compile("FAILURE.+")
        if bool(re.match(err_regex, json_response["status"])):
            logger.error(f"Error {json_response['statusMessage']}")
            raise AuthenticationFailedError(
                f"Error logging in {json_response['statusMessage']}"
            )

        token = json_response["tokenInfo"]["tokenValue"]
        expires = json_response["tokenInfo"]["expiresAt"]
        status = AnaplanAuthentication.verify_auth(token)

        if status != "Token validated":
            logger.error(f"Error {status}")
            raise AuthenticationFailedError(f"Error getting authentication {status}")

        logger.info("User successfully authenticated.")
        return AuthToken(f"AnaplanAuthToken {token}", expires)

    @staticmethod
    def verify_auth(token: str) -> str:
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
            validate = json.loads(
                requests.get(anaplan_url, headers=header, timeout=(5, 30)).text
            )
        except (
            HTTPError,
            ConnectionError,
            SSLError,
            Timeout,
            ConnectTimeout,
            ReadTimeout,
        ) as e:
            logger.error(f"Error verifying auth token {e}", exc_info=True)
            raise Exception(f"Error verifying auth token {e}")
        except ValueError as e:
            logger.error(f"Error loading response JSON {e}", exc_info=True)
            raise ValueError(f"Error loading response JSON {e}")

        if "statusMessage" in validate:
            return validate["statusMessage"]

    @staticmethod
    def refresh_token(token: str, auth_object: AuthToken):
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
            refresh = json.loads(
                requests.post(url, headers=header, timeout=(5, 30)).text
            )
        except (
            HTTPError,
            ConnectionError,
            SSLError,
            Timeout,
            ConnectTimeout,
            ReadTimeout,
        ) as e:
            logger.error(f"Error verifying auth token {e}", exc_info=True)
            raise Exception(f"Error verifying auth token {e}")
        except ValueError as e:
            logger.error(f"Error loading response JSON {e}", exc_info=True)
            raise ValueError(f"Error loading response JSON {e}")

        if "tokenInfo" in refresh:
            if "tokenValue" in refresh["tokenInfo"]:
                new_token = refresh["tokenInfo"]["tokenValue"]
            if "expiresAt" in refresh["tokenInfo"]:
                new_expiry = refresh["tokenInfo"]["expiresAt"]

        auth_object.set_auth_token("".join(["AnaplanAuthToken ", new_token]))
        auth_object.set_token_expiry(new_expiry)
