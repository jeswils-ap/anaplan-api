# ===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
# ===========================================================================
import pandas as pd
import logging
from distutils.util import strtobool
from .Parser import Parser
from .ParserResponse import ParserResponse

logger = logging.getLogger(__name__)


class ImportParser(Parser):
	results: ParserResponse

	def __init__(self, results: dict, url: str):
		ImportParser.results = ImportParser.parse_response(results, url)

	@staticmethod
	def get_results():
		return ImportParser.results

	@staticmethod
	def parse_response(results: dict, url: str) -> ParserResponse:
		"""
		:param results: JSON dictionary of task results
		:param url: URL of Anaplan task
		:return: Array with overall task result as string, file contents in string,
				boolean if error dump is available, and dataframe with error dump.
		"""

		# Create placeholder objects
		edf = pd.DataFrame()
		msg = []

		logger.debug("Parsing import details")

		job_status = results['currentStep']
		failure_dump = bool(strtobool(str(results['result']['failureDumpAvailable']).lower()))

		if job_status == "Failed.":
			return Parser.failure_message(results)
		else:
			# IF failure dump is available download
			if failure_dump:
				edf = Parser.get_dump(''.join([url, "/dump"]))

			success_report = str(results['result']['successful'])

			# details key only present in import task results
			if 'details' in results['result']:
				logger.info("Fetching import details.")
				for i in range(0, len(results['result']['details'])):
					if 'localMessageText' in results['result']['details'][i]:
						msg.append(str(results['result']['details'][i]['localMessageText']))
						if 'values' in results['result']['details'][i]:
							for detail in results['result']['details'][i]['values']:
								msg.append(detail)

			logger.info(f"The requested job is {job_status}")
			logger.info(f"Failure Dump Available: {failure_dump}, Successful: {success_report}")

			return ParserResponse('\n'.join(msg), "", failure_dump, edf)
