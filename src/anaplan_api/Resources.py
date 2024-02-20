import logging
import requests
import json
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from .AnaplanConnection import AnaplanConnection
from .util.Util import ResourceNotFoundError, RequestFailedError
from .util.AnaplanVersion import AnaplanVersion

logger = logging.getLogger(__name__)


class Resources:
    _authorization: str
    _resource: str
    _workspace: str
    _model: str
    _base_url = f"https://api.anaplan.com/{AnaplanVersion.major}/{AnaplanVersion.minor}/workspaces/"
    _url: str

    def __init__(self, conn: AnaplanConnection, resource: str):
        """
        :param conn: Object with authentication, workspace, and model details
        :type conn: AnaplanConnection
        :param resource: Type of resource to query the specified model for
        :type resource: str
        """
        self._authorization = conn.get_auth().get_auth_token()
        self._workspace = conn.get_workspace()
        self._model = conn.get_model()
        self._url = ''.join([self._base_url, self._workspace, "/models/", self._model, "/", resource])
        valid_resources = ["imports", "exports", "actions", "processes", "files", "lists"]
        if resource.lower() in valid_resources:
            self._resource = resource.lower()
        else:
            raise ResourceNotFoundError(f"Invalid selection, resource must be one of {', '.join(valid_resources)}")

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
            'Authorization': authorization,
            'Content-Type': 'application/json'
        }

        response = {}

        logger.debug(f"Fetching {self._resource}")
        try:
            response = json.loads(requests.get(self._url, headers=get_header, timeout=(5, 30)).text)
        except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
            logger.error(f"Error fetching resource {self._resource}, {e}", exc_info=True)
        logger.debug(f"Finished fetching {self._resource}")

        if 'status' in response:
            if 'code' in response['status']:
                if response['status']['code'] == 200:
                    if self._resource in response:  # If the specified resource is found in the response return the list
                        return response[self._resource]
                else:
                    raise RequestFailedError(f"Request was unsuccessful, code: {response['status']['code']}")
            else:
                raise KeyError("code not found in response")
        else:
            raise KeyError("status not found in response")
