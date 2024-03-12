# ===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
# ===========================================================================
import pandas as pd
import logging
from typing import List
from .util.strtobool import strtobool
from .Parser import Parser
from .models.ParserResponse import ParserResponse

logger = logging.getLogger(__name__)


class ImportParser(Parser):
    _results: List[ParserResponse] = list()

    def __init__(self, conn, results: dict, url: str):
        super().__init__(conn, results=results, url=url)
        self._results.extend(ImportParser.parse_response(conn, results, url))

    @staticmethod
    def get_results() -> List[ParserResponse]:
        """Fetch parsed results for the specified task

        :return: Object containing parsed task results and related data
        :rtype: List[ParserResponse]
        """
        return ImportParser._results

    @staticmethod
    def parse_response(conn, results: dict, url: str) -> List[ParserResponse]:
        """Convert JSON response into uniform task result, with error details and related data
        :param conn: Object with authentication, workspace, and model details
        :type conn: AnaplanConnection
        :param results: JSON dictionary of task results
        :type results: dict
        :param url: URL of Anaplan task
        :type url: str
        :return: Object containing overall task result as string, file contents in string if applicable,
                         boolean if error dump is available, and dataframe with error dump.
        :rtype: ParserResponse
        """

        # Create placeholder objects
        edf = pd.DataFrame()
        msg = []

        logger.debug("Parsing import details")
        logger.debug(results)

        job_status = results["currentStep"]
        failure_dump = bool(
            strtobool(str(results["result"]["failureDumpAvailable"]).lower())
        )

        if job_status == "Failed.":
            logger.error(f"Job failed with status {job_status}")
            return Parser.failure_message(results)
        else:
            # IF failure dump is available download
            if failure_dump:
                edf = super().get_dump("".join([url, "/dump"]))

            success_report = str(results["result"]["successful"])

            # details key only present in import task results
            if "details" in results["result"]:
                logger.info("Fetching import details.")
                for i in range(0, len(results["result"]["details"])):
                    if "localMessageText" in results["result"]["details"][i]:
                        msg.append(
                            str(results["result"]["details"][i]["localMessageText"])
                        )
                        if "values" in results["result"]["details"][i]:
                            for detail in results["result"]["details"][i]["values"]:
                                msg.append(detail)

            logger.info(f"The requested job is {job_status}")
            logger.info(
                f"Failure Dump Available: {failure_dump}, Successful: {success_report}"
            )

            return [ParserResponse("\n".join(msg), "", failure_dump, edf)]
