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
	"""Represents a parser for Anaplan actions. This class parses and stores the results of an Anaplan task.

	:param results: ParserResponse object with the details of an executed Anaplan task
	:type results: List[ParserResponse]
	"""
	results: List[ParserResponse]

	def __init__(self, results: dict, url: str):
		"""This Parser class does not require a AnaplanConnection object because this action type does not generate
		an error dump, nor output a file that would require further API calls.

		:param results: JSON response object with the details of an executed action
		:type results: dict
		:param url: URL of the executed action
		:type url: str
		"""
		super().__init__(results=results, url=url)
		ActionParser.results.append(ActionParser.parse_response(results, url))

	@staticmethod
	def get_results() -> List[ParserResponse]:
		"""Get the results of the Anaplan task

		:return: List of ParserResponse objects
		"""
		return ActionParser.results

	@staticmethod
	def parse_response(results: dict, url: str) -> ParserResponse:
		"""Creates a ParserResponse object with JSON task results converted into a standardized response.

		:param results: JSON dump of the results of an Anaplan action
		:type results: dict
		:param url: URL of the Anaplan task
		:type url: str
		:return: ParserResponse object with details of an executed action
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
