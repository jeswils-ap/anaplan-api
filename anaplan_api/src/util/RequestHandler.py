import logging
import requests
from requests.exceptions import (
    HTTPError,
    ConnectionError,
    SSLError,
    Timeout,
    ConnectTimeout,
    ReadTimeout,
)
from typing import Union

logger = logging.getLogger(__name__)


class RequestHandler:
    _base_url: str

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data=None,
        headers=None,
        override_url=None,
    ) -> requests.Response:
        url: str = override_url if override_url else self._base_url + endpoint
        response: Union[requests.Response | None] = None
        try:
            response = requests.request(
                method, url, data=data, headers=headers, timeout=(5, 30)
            )
        except (
            HTTPError,
            ConnectionError,
            SSLError,
            Timeout,
            ConnectTimeout,
            ReadTimeout,
        ) as e:
            logger.error(f"Error with API request {e}", exc_info=True)

        return response
