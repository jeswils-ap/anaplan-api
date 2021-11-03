#===========================================================================
# This function reads the JSON results of the completed Anaplan task and returns
# the job details.
#===========================================================================
import logging, re
import pandas as pd
from io import StringIO
from distutils.util import strtobool
import anaplan_api.anaplan
from anaplan_api.AnaplanConnection import AnaplanConnection
from anaplan_api.Parser import Parser

logger = logging.getLogger(__name__)


class ProcessParser(Parser):
	results = []
	authorization: str

	def __init__(self, conn: AnaplanConnection, results: dict, url: str):
		self.authorization = conn.get_auth()
		ProcessParser.results = ProcessParser.parse_response(conn, results, url).copy()

	@staticmethod
	def get_results():
		return ProcessParser.results

	def parse_response(conn: AnaplanConnection, results: dict, url: str):
		'''
		:param conn: AnaplanConnection object
		:param results: JSON dump of the results of an Anaplan action
		:param: url Base url for task
		:param: task_id: 32-characher ID for task
		:param: post_header: Header string with authentication
		:returns: Array with String of overall task result, and array of process action details)
		'''
		
		job_status = results['currentStep']
		failure_alert = bool(strtobool(str(results['result']['failureDumpAvailable']).lower()))

		if job_status == "Failed.":
			logger.error("The task has failed to run due to an error, please check process definition in Anaplan")
			return ("The task has failed to run due to an error, please check process definition in Anaplan", None)
		else:
			logger.info("Process completed.")
			#nestedResults key only present in process task results
			if 'nestedResults' in results['result']:
				nested_details = []
				
				logger.debug("Parsing nested results.")
				for nestedResults in results['result']['nestedResults']:
					#Array to store sub-process import details
					subprocess_detail = []

					subprocess_failure = str(nestedResults['failureDumpAvailable'])
					object_id = str(nestedResults['objectId'])
					subprocess_msg = f"Process action {object_id} completed. Failure: {subprocess_failure}"

					logger.info(f"Fetching details for object {object_id}")
					objectDetails = ProcessParser.sub_process_parser(conn, object_id, nestedResults, url)
					nested_details.append([objectDetails[0], objectDetails[1], objectDetails[2]])

				return nested_details

	def sub_process_parser(conn: AnaplanConnection, object_id: str, results: dict, url: str):
		#Create placeholders objects
		eDf = pd.DataFrame()
		msg = []

		#Regex pattern for hierarchy parsing
		hReg = re.compile('hierarchyRows.+')

		failure_dump = bool(strtobool(str(results['failureDumpAvailable']).lower()))
		successful = results['successful']

		if failure_dump:
			eDf = super().get_dump(''.join([url, '/dumps/', object_id]))

		#Import specific parsing
		if 'details' in results:
			for i in range(0, len(results['details'])):
				#Import specific parsing
				if 'localMessageText' in results['details'][i]:
					msg.append(results['details'][i]['localMessageText'])
					#Parsing module imports with failures
					if 'values' in results['details'][i]:
						for j in range(0, len(results['details'][i]['values'])):
							msg.append(results['details'][i]['values'][j])
				if 'type' in results['details'][i]:
					#Parsing hierarchy import nested details
					if bool(re.match(hReg, results['details'][i]['type'])):
						if 'values' in results['details'][i]:
							for j in range(0, len(results['details'][i]['values'])):
								msg.append(results['details'][i]['values'][j])
				#Export specific parsing
				if 'type' in results['details'][i]:
					if results['details'][i]['type'] == "exportSucceeded":
						msg = anaplan.get_file(conn, object_id)


		logger.debug(f"Error dump available: {failure_dump}, Sub-task {object_id} successful: {successful}")
		return [f"Error dump available: {failure_dump}, Sub-task {object_id} successful: {successful}", '\n'.join(msg), eDf]
