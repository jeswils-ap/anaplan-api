# ===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
# ===========================================================================
import logging
import re
import pandas as pd
from distutils.util import strtobool
from typing import List
from anaplan_api import anaplan
from .AnaplanConnection import AnaplanConnection
from .Parser import Parser
from .ParserResponse import ParserResponse

logger = logging.getLogger(__name__)


class ProcessParser(Parser):
    results: List[ParserResponse]
    authorization: str

    def __init__(self, conn: AnaplanConnection, results: dict, url: str):
        self.authorization = conn.get_auth()
        ProcessParser.results = ProcessParser.parse_response(conn, results, url).copy()

    @staticmethod
    def get_results() -> List[ParserResponse]:
        return ProcessParser.results

    @staticmethod
    def parse_response(conn: AnaplanConnection, results: dict, url: str) -> List[ParserResponse]:
        """

        :param conn: AnaplanConnection object
        :param results: JSON dictionary of results to parse
        :param url: URL of Anaplan task
        :return: ParserResponse object
        """

        job_status = results['currentStep']

        if job_status == "Failed.":
            logger.error("The task has failed to run due to an error, please check process definition in Anaplan")
            return [ParserResponse("The task has failed, check process definition in Anaplan", "", False, pd.DataFrame())]
        else:
            logger.info("Process completed.")
            # nestedResults key only present in process task results
            if 'nestedResults' in results['result']:
                nested_details = [ParserResponse]

                logger.debug("Parsing nested results.")
                for nestedResults in results['result']['nestedResults']:
                    object_id = str(nestedResults['objectId'])

                    logger.debug(f"Fetching details for object {object_id}")
                    nested_details.append(ProcessParser.sub_process_parser(conn, object_id, nestedResults, url))

                return nested_details

    @staticmethod
    def sub_process_parser(conn: AnaplanConnection, object_id: str, results: dict, url: str) -> ParserResponse:
        # Create placeholders objects
        edf = pd.DataFrame()
        msg = []
        export_file = ""

        # Regex pattern for hierarchy parsing
        regex = re.compile('hierarchyRows.+')

        failure_dump = bool(strtobool(str(results['failureDumpAvailable']).lower()))
        successful = results['successful']

        if failure_dump:
            edf = super().get_dump(''.join([url, '/dumps/', object_id]))

        # Import specific parsing
        if 'details' in results:
            for i in range(0, len(results['details'])):
                # Import specific parsing
                if 'localMessageText' in results['details'][i]:
                    msg.append(results['details'][i]['localMessageText'])
                    # Parsing module imports with failures
                    if 'values' in results['details'][i]:
                        for j in range(0, len(results['details'][i]['values'])):
                            msg.append(results['details'][i]['values'][j])
                if 'type' in results['details'][i]:
                    # Parsing hierarchy import nested details
                    if bool(re.match(regex, results['details'][i]['type'])):
                        if 'values' in results['details'][i]:
                            for j in range(0, len(results['details'][i]['values'])):
                                msg.append(results['details'][i]['values'][j])
                    # Export specific parsing
                    if results['details'][i]['type'] == "exportSucceeded":
                        export_file = anaplan.get_file(conn, object_id)

        logger.debug(f"Error dump available: {failure_dump}, Sub-task {object_id} successful: {successful}")
        return ParserResponse('\n'.join(msg), export_file, failure_dump, edf)
