# ===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
# ===========================================================================
import pandas as pd
import logging
from typing import List
from distutils.util import strtobool
from .Parser import Parser
from .ParserResponse import ParserResponse

logger = logging.getLogger(__name__)


class ActionParser(Parser):
	results: List[ParserResponse]

	def __init__(self, results: dict, url: str):
		super().__init__(results=results, url=url)
		ActionParser.results.append(ActionParser.parse_response(results, url))

	@staticmethod
	def get_results():
		return ActionParser.results

	@staticmethod
	def parse_response(results: dict, url: str) -> ParserResponse:
		"""
		:param url:
		:param results: JSON dump of the results of an Anaplan action
		:return: Array with overall task result as string, file contents in string,
				boolean if error dump is available, and dataframe with error dump.
		"""

		job_status = results['currentStep']
		failure_dump = bool(strtobool(str(results['result']['failureDumpAvailable']).lower()))
		edf = pd.DataFrame()

		if job_status == "Failed.":
			return Parser.failure_message(results)
		else:
			# IF failure dump is available download
			if failure_dump:
				edf = Parser.get_dump(''.join([url, "/dump"]))

			success_report = str(results['result']['successful'])

			# details key only present in import task results
			if 'objectId' in results['result']:
				object_id = results['result']['objectId']
				action_detail = f"{object_id} completed successfully: {success_report}"

				logger.info(f"The requested job is {job_status}")
				logger.info(f"Failure Dump Available: {failure_dump}, Successful: {success_report}")

				return ParserResponse(action_detail, "", failure_dump, edf)
