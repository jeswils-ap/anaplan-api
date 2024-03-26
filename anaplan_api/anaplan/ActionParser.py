# ===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
# ===========================================================================
from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from typing import List
from .util.strtobool import strtobool
from .Parser import Parser
from .models.ParserResponse import ParserResponse

if TYPE_CHECKING:
    from .models.AnaplanConnection import AnaplanConnection

logger = logging.getLogger(__name__)


class ActionParser(Parser):
    """
    This class is a specific implementation for parsing the results of Anaplan Action type tasks.
    """

    def parse_response(
        self, conn: AnaplanConnection, results: dict, url: str
    ) -> List[ParserResponse]:
        """Creates a ParserResponse object with JSON task results converted into a standardized response.
        :param conn: AnaplanConnection object containing Workspace and Model ID, and AuthToken object
        :type conn: AnaplanConnection
        :param results: JSON dump of the results of an Anaplan action
        :type results: dict
        :param url: URL of the Anaplan task
        :type url: str
        :return: ParserResponse object with details of an executed action
        """

        job_status = results["currentStep"]
        failure_dump = strtobool(str(results["result"]["failureDumpAvailable"]).lower())

        """Should never happen for Action type tasks"""
        if job_status == "Failed.":
            return self.failure_message(results)

        success_report = str(results["result"]["successful"])

        # details key only present in import task results
        if "objectId" not in results["result"]:
            raise KeyError("'objectId' could not be found in response.")

        object_id = results["result"]["objectId"]
        action_detail = f"{object_id} completed successfully: {success_report}"

        logger.info(f"The requested job is {job_status}")
        logger.info(
            f"Failure Dump Available: {failure_dump}, Successful: {success_report}"
        )

        return [
            ParserResponse(
                results, action_detail, self.endpoint, "", failure_dump, False
            )
        ]
