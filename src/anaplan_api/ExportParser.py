# ===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
# ===========================================================================
from anaplan_api import anaplan
import pandas as pd
import logging
from distutils.util import strtobool
from .Parser import Parser
from .AnaplanConnection import AnaplanConnection
from .ParserResponse import ParserResponse


logger = logging.getLogger(__name__)


class ExportParser(Parser):
	results: ParserResponse

	def __init__(self, conn: AnaplanConnection, results: dict, url: str):
		ExportParser.results = ExportParser.parse_response(conn, results, url)

	@staticmethod
	def get_results():
		return ExportParser.results

	@staticmethod
	def parse_response(conn, results, url) -> ParserResponse:
		"""
		:param conn: AnaplanConnection
		:param results: JSON dict with task results.
		:param url: URL of Anaplan task
		:return: Array with overall task result as string, file contents in string,
				boolean if error dump is available, and dataframe with error dump.
		"""
		'''
		:param results: JSON dump of the results of an Anaplan action
		:returns: String with task details, file contents as String, and an array of error dump dataframes
		'''

		job_status = results['currentStep']
		failure_dump = bool(strtobool(str(results['result']['failureDumpAvailable']).lower()))
		edf = pd.DataFrame()

		if job_status == "Failed.":
			'''Should Never happen for Export type tasks'''
			return Parser.get_dump(results)
		else:
			# IF failure dump is available download
			if failure_dump:
				edf = Parser.get_dump(''.join([url, "/dump"]))

			success_report = str(results['result']['successful'])

			# details key only present in import task results
			if 'objectId' in results['result']:
				object_id = results['result']['objectId']
				file_contents = anaplan.get_file(conn, object_id)

				logger.info(f"The requested job is {job_status}")
				logger.error(f"Failure Dump Available: {failure_dump}, Successful: {success_report}")

				return ParserResponse("File export completed.", file_contents, False, edf)
