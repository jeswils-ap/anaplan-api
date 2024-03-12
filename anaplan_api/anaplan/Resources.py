from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from .util.RequestHandler import RequestHandler
from .models.AnaplanVersion import AnaplanVersion
from .util.Util import ResourceNotFoundError, RequestFailedError

if TYPE_CHECKING:
    from .models.AnaplanConnection import AnaplanConnection

logger = logging.getLogger(__name__)


class Resources:
    """Fetches the list of request resource type from a specified Anaplan model
    :param _handler: Class for sending API requests
    :type _handler: RequestHandler
    :param _authorization: AnaplanAuthToken value
    :type _authorization: str
    :param _resource: Name of the type of resource to fetch details from Anaplan model
    :type _resource: str
    :param _workspace: Anaplan model's workspace ID
    :type _workspace: str
    :param _model: Anaplan model ID
    :type _model: str
    :param _base_endpoint: Starting endpoint for all resource requests
    :type _base_endpoint: str
    :param _endpoint: API endpoint used to fetch the list of specified resources from an Anaplan model
    :type _endpoint: str
    """

    _handler: RequestHandler = RequestHandler(AnaplanVersion().base_url)
    _authorization: str
    _resource: str
    _workspace: str
    _model: str
    _base_endpoint = f"workspaces/"
    _endpoint: str

    def __init__(self, conn: AnaplanConnection, resource: str):
        """
        :param conn: Object with authentication, workspace, and model details
        :type conn: AnaplanConnection
        :param resource: Type of resource to query the specified model for
        :type resource: str
        """
        self._authorization = conn.authorization.token_value
        self._workspace = conn.workspace
        self._model = conn.model
        self._endpoint = (
            f"{self._base_endpoint}{self._workspace}/models/{self._model}/{resource}"
        )
        valid_resources = [
            "imports",
            "exports",
            "actions",
            "processes",
            "files",
            "lists",
        ]

        if resource.lower() not in valid_resources:
            raise ResourceNotFoundError(
                f"Invalid selection, resource must be one of {', '.join(valid_resources)}"
            )

        self._resource = resource.lower()

    def get_resources(self) -> dict:
        """Get the list of items of the specified resource

        :raises HTTPError: HTTP error code
        :raises ConnectionError: Network-related errors
        :raises SSLError: Server-side SSL certificate errors
        :raises Timeout: Request timeout errors
        :raises ConnectTimeout: Timeout error when attempting to connect
        :raises ReadTimeout: Timeout error waiting for server response
        :raises RequestFailedError: Error returned by Anaplan API server for specified request
        :raises KeyError: Error if response does not contain the specified resource
        :return: JSON list of the specified resource
        """
        authorization = self._authorization

        get_header = {
            "Authorization": authorization,
            "Content-Type": "application/json",
        }

        response = {}

        logger.debug(f"Fetching {self._resource}")
        try:
            response = self._handler.make_request(
                self._endpoint, headers=get_header
            ).json()
        except Exception as e:
            logger.error(
                f"Error fetching resource {self._resource}, {e}", exc_info=True
            )
        logger.debug(f"Finished fetching {self._resource}")

        if "status" not in response or "code" not in response["status"]:
            raise KeyError(f"Status or code not found in response: {response}")

        if response["status"]["code"] != 200:
            raise RequestFailedError(
                f"Request was unsuccessful, code: {response['status']['code']}"
            )

        if self._resource not in response:
            raise KeyError(f"Resource {self._resource} not found in response")

        return response[self._resource]
