# ===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
# ===========================================================================
from __future__ import annotations
from typing import List, TYPE_CHECKING
import pandas as pd
import logging
from .util.strtobool import strtobool
from . import anaplan
from .Parser import Parser
from .models.ParserResponse import ParserResponse

if TYPE_CHECKING:
    from .models.AnaplanConnection import AnaplanConnection


logger = logging.getLogger(__name__)


class ExportParser(Parser):
    _results: List[ParserResponse] = list()

    @property
    def results(self) -> List[ParserResponse]:
        """Get the list of task result details

        :return: Formatted export task results
        :rtype: List[ParserResponse]
        """
        return self._results

    def parse_response(self, conn, results, url) -> List[ParserResponse]:
        """Parse the JSON response for a task into an object with standardized format.
        :param conn: AnaplanConnection object with authentication, workspace and model IDs
        :type conn: AnaplanConnection
        :param results: JSON dict with task results.
        :type results: dict
        :param url: URL of Anaplan task
        :type url: str
        :return: Array with overall task result as string, file contents in string,
                        boolean if error dump is available, and dataframe with error dump.
        :rtype: ParserResponse
        """

        job_status = results["currentStep"]
        failure_dump = bool(
            strtobool(str(results["result"]["failureDumpAvailable"]).lower())
        )
        edf = pd.DataFrame()

        """Should never happen for Export type tasks"""
        if job_status == "Failed.":
            return self.failure_message(results)
        if failure_dump:
            edf = self.get_dump(f"{url}/dump")

        success_report = str(results["result"]["successful"])

        if "objectId" not in results["result"]:
            raise KeyError("'objectId' could not be found in response.")

        # details key only present in import task results
        object_id = results["result"]["objectId"]
        file_contents = anaplan.get_file(conn, object_id)

        logger.info(f"The requested job is {job_status}")
        logger.info(
            f"Failure Dump Available: {failure_dump}, Successful: {success_report}"
        )

        return [ParserResponse("File export completed.", file_contents, False, edf)]
