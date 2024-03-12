from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from anaplan_api.src.models.UserDetails import UserDetails
from anaplan_api.src.util.RequestHandler import RequestHandler
from anaplan_api.src.models.AnaplanVersion import AnaplanVersion

if TYPE_CHECKING:
    from anaplan_api.src.models.AnaplanConnection import AnaplanConnection

logger = logging.getLogger(__name__)


class User:
    """
    Class representing an Anaplan user
    """

    _endpoint: str = f"users/"
    _handler: RequestHandler = RequestHandler(AnaplanVersion().base_url)
    _conn: AnaplanConnection
    _user_id: str
    _user_details: UserDetails
    _raw_data: dict

    def __init__(
        self, conn: AnaplanConnection, user_id: str = None
    ):
        """
        :param conn: Object containing Workspace and Model ID, and AuthToken object
        :type conn: AnaplanConnection
        :param user_id: ID of specified user
        :type user_id: str
        """
        self._conn = conn
        self._user_id = user_id

    def get_current_user(self):
        """Get the ID of the current user

        :raises HTTPError: HTTP error code
        :raises ConnectionError: Network-related errors
        :raises SSLError: Server-side SSL certificate errors
        :raises Timeout: Request timeout errors
        :raises ConnectTimeout: Timeout error when attempting to connect
        :raises ReadTimeout: Timeout error waiting for server response
        :raises ValueError: Error loading text response to JSON
        :raises KeyError: Error locating User or ID key in JSON response.
        """
        if self._user_id is not None:
            return

        url = f"{self.endpoint}me"
        authorization = self.conn.authorization.token_value

        get_header = {"Authorization": authorization}

        logger.debug("Fetching user ID.")

        try:
            logger.debug("Retrieving details of current user.")
            user_details = self._handler.make_request(
                url, "GET", headers=get_header
            ).json()
        except Exception as e:
            logger.error(f"Error fetching user details {e}", exc_info=True)
            raise Exception(f"Error fetching user details {e}")

        if "user" not in user_details:
            raise KeyError("'user' not found in response")
        if "id" not in user_details["user"]:
            raise KeyError("'id' not found in response")

        self._user_id = user_details["user"]["id"]
        self._raw_data = user_details["user"]
        self._user_details = UserDetails(user_details["user"])

    def get_user_details(self):
        """Get details of the specified user

        :raises Exception: Error from the RequestHandler exception group
        :raises KeyError: Error locating User or ID key in JSON response.
        """
        if self._user_id is not None:
            return

        url = f"{self.endpoint}{self.id}"
        authorization = self.conn.authorization.token_value

        get_header = {"Authorization": authorization}

        logger.debug("Fetching user ID.")

        try:
            logger.debug("Retrieving details of current user.")
            user_details = self._handler.make_request(
                url, "GET", headers=get_header
            ).json()
        except Exception as e:
            logger.error(f"Error fetching user details {e}", exc_info=True)
            raise Exception(f"Error fetching user details {e}")

        if "user" not in user_details:
            raise KeyError("'user' not found in response")
        if "id" not in user_details["user"]:
            KeyError("'id' not found in response")

        self._user_id = user_details["user"]["id"]
        self._user_details = UserDetails(user_details["user"])

    @property
    def conn(self) -> AnaplanConnection:
        """Get AnaplanConnection object

        :return: AnaplanConnection object for current user
        :rtype: AnaplanConnection
        """
        return self._conn

    @property
    def endpoint(self) -> str:
        """Get base URL for user requests

        :return: User details url
        :rtype: str
        """
        return self._endpoint

    @property
    def id(self) -> str:
        """Get ID of the specified user

        :return: User ID
        :rtype: str
        """
        return self._user_id

    @property
    def user(self) -> UserDetails:
        """Get details for the specified user

        :return: Friendly user details
        :rtype: UserDetails
        """
        return self._user_details

    def get_models(self):
        """Get list of models for a user"""

    def get_workspace(self):
        """Get list of workspaces for a user"""
