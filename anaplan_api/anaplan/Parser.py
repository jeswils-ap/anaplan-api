# ===============================================================================
# Created:			29 Oct 2021
# @author:			Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:		Generic class to parse Anaplan API task responses
# Input:			JSON array of task results, URL of Anaplan task, Task ID string,
# 					Request header string
# Output:			Array containing overall task results string, details results string,
# 					error dump dataframe.
# ===============================================================================
from __future__ import annotations
from typing import List, TYPE_CHECKING
import logging
from .models.ParserResponse import ParserResponse
from .util.RequestHandler import RequestHandler
from .models.AnaplanVersion import AnaplanVersion

if TYPE_CHECKING:
    from .models.AnaplanConnection import AnaplanConnection

logger = logging.getLogger(__name__)


class Parser(object):
    """Represents a generic Parser object that parses the task results of an Anaplan AnaplanConnection

    :param _handler: Class used to handle API requests
    :type _handler: RequestHandler
    :param _results: List of ParserResponse objects containing details of an Anaplan task
    :type _results: List[ParserResponseNew]
    :param _authorization: Header containing Authorization and Content-Type for API requests
    :type _authorization: str
    """

    _handler: RequestHandler = RequestHandler(AnaplanVersion().base_url)
    _results: List[ParserResponse] = list()
    _authorization: str
    _endpoint: str

    def __init__(
        self,
        conn: AnaplanConnection,
        results: dict,
        url: str,
    ):
        """
        :param conn: AnaplanConnection object containing Workspace and Model ID, and AuthToken object
        :type conn: AnaplanConnection
        :param results: JSON task results of an executed Anaplan action
        :type results: dict
        :param url: URL of the Anaplan action task
        :type url: str
        """
        self._authorization = conn.authorization.token_value
        self._endpoint = url
        self._results.extend(self.parse_response(conn, results, url))

    @property
    def results(self) -> List[ParserResponse]:
        """Get details of Anaplan action task

        :return: Friendly results of an executed task, including status, file and error dump if applicable
        :rtype: List[ParserResponseNew]
        """
        return self._results

    @property
    def endpoint(self) -> str:
        return self._endpoint

    def parse_response(
        self, conn: AnaplanConnection, results: dict, url: str
    ) -> List[ParserResponse]:
        pass

    def failure_message(self, results: dict) -> List[ParserResponse]:
        """Creates a ParserResponse in case of an Action failure
        :param results: JSON task results of an executed Anaplan action
        :type results: dict
        :return: Generic response for failed tasks.
        :rtype: List[ParserResponse]
        """

        responses: List[ParserResponse] = list()

        if "result" not in results or "details" not in results["result"]:
            raise KeyError(f"Unable to find result or details in response: {results}")

        for i in range(0, len(results["result"]["details"])):
            if "localMessageText" not in results["result"]["details"][i]:
                continue

            error_message = str(results["result"]["details"][i]["localMessageText"])
            logger.warning(
                f"The task has failed to run due to an error: {error_message}"
            )
            responses.append(
                ParserResponse(
                    results,
                    f"The task has failed to run due to an error: {error_message}",
                    self.endpoint,
                    "",
                    False,
                    False,
                )
            )
        return responses
