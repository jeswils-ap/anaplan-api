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
    _base_url = f"https://api.anaplan.com/{AnaplanVersion.major()}/{AnaplanVersion.minor()}/workspaces/"
    _url: str

    def __init__(self, conn: AnaplanConnection, resource: str):
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
                    if self._resource in response:
                        return response[self._resource]
                else:
                    raise RequestFailedError(f"Request was unsuccessful, code: {response['status']['code']}")
            else:
                raise KeyError("code not found in response")
        else:
            raise KeyError("status not found in response")
