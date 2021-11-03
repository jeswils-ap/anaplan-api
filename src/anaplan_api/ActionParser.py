#===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
#===========================================================================
import logging
import pandas as pd
from io import StringIO
from distutils.util import strtobool
from anaplan_api.Parser import Parser

logger = logging.getLogger(__name__)


class ActionParser(Parser):
	results = []

	def __init__(self, results: dict, url: str):
		ActionParser.results = ActionParser.parse_response(results, url).copy()

	@staticmethod
	def get_results():
		return ActionParser.results

	def parse_response(results: dict, url: str):
		'''
		:param results: JSON dump of the results of an Anaplan action
		:returns: String with task details, action details as String, and an array of error dump dataframes
		'''

		job_status = results['currentStep']
		failure_dump = bool(strtobool(str(results['result']['failureDumpAvailable']).lower()))
		eDf = pd.DataFrame()
		
		if job_status == "Failed.":
			return Parser.failure_message(results)
		else:
			#IF failure dump is available download
			if failure_dump:
				eDf = Parser.get_dump(''.join([url, "/dump"]))
			
			success_report = str(results['result']['successful'])
			
			#details key only present in import task results
			if 'objectId' in results['result']:
				object_id = results['result']['objectId']
				action_detail = f"{object_id} completed successfully: {success_report}"

				logger.info(f"The requested job is {job_status}")
				logger.error(f"Failure Dump Available: {failure_dump}, Successful: {success_report}")

				return [f"Failure Dump Available: {failure_dump}, Successful: {success_report}", action_detail, error_dumps]
