import logging
import requests
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from typing import Union

logger = logging.getLogger(__name__)


class RequestHandler:
    _base_url: str

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    def make_request(self, endpoint: str, method: str = 'GET', data=None, headers=None) -> requests.Response:
        url: str = self._base_url + endpoint
        response: Union[requests.Response | None] = None
        try:
            logger.debug("Fetching error dump")
            response = requests.request(method, url, data=data, headers=headers, timeout=(5, 30))
            dump = requests.get(''.join([url, "/dump"]), headers=headers, timeout=(5, 30)).text
            logger.debug("Error dump downloaded.")
        except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
            logger.error(f"Error fetching error dump {e}", exc_info=True)

        return response

