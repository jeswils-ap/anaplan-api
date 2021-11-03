#===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
#===========================================================================
import logging
import pandas as pd
from io import StringIO
from distutils.util import strtobool
import anaplan_api.anaplan
from anaplan_api.Parser import Parser
from anaplan_api.AnaplanConnection import AnaplanConnection

logger = logging.getLogger(__name__)


class ExportParser(Parser):

	results = []

	def __init__(self, conn: AnaplanConnection, results: dict, url: str):
		ExportParser.results = ExportParser.parse_response(conn, results, url).copy()

	@staticmethod
	def get_results():
		return ExportParser.results

	def parse_response(conn, results, url):
		'''
		:param results: JSON dump of the results of an Anaplan action
		:returns: String with task details, file contents as String, and an array of error dump dataframes
		'''
		
		job_status = results['currentStep']
		failure_dump = bool(strtobool(str(results['result']['failureDumpAvailable']).lower()))
		eDf = pd.DataFrame()
		
		if job_status == "Failed.":
			'''Should Never happen for Export type tasks'''
			return Parser.get_dump(results)
		else:
			#IF failure dump is available download
			if failure_dump:
				eDf = Parser.get_dump(''.join([url, "/dump"]))

			success_report = str(results['result']['successful'])
			
			#details key only present in import task results
			if 'objectId' in results['result']:
				object_id = results['result']['objectId']
				file_contents = anaplan.get_file(conn, object_id)

				logger.info(f"The requested job is {job_status}")
				logger.error(f"Failure Dump Available: {failure_dump}, Successful: {success_report}")
				
				return (f"Failure Dump Available: {failure_dump}, Successful: {success_report}", file_contents, eDf)
