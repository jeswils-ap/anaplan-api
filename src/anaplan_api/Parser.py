# ===============================================================================
# Created:			29 Oct 2021
# @author:			Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:		Generic class to parse Anaplan API task responses
# Input:			JSON array of task results, URL of Anaplan task, Task ID string,
# 					Request header string
# Output:			Array containing overall task results string, details results string,
# 					error dump dataframe.
# ===============================================================================
import logging
import requests
import pandas as pd
from io import StringIO
from typing import List, Optional
from pandas import DataFrame
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from pandas.errors import EmptyDataError, ParserError, ParserWarning
from .AnaplanConnection import AnaplanConnection
from .ParserResponse import ParserResponse

logger = logging.getLogger(__name__)


class Parser(object):
	"""Represents a generic Parser object that parses the task results of an Anaplan AnaplanConnection

	:param _results: List of ParserResponse objects containing details of an Anaplan task
	:type _results: List[ParserResponse]
	:param _authorization: Header containing Authorization and Content-Type for API requests
	:type _authorization: str
	"""
	_results: List[ParserResponse]
	_authorization: str

	def __init__(self, conn: Optional[AnaplanConnection], results: dict, url: str):
		"""
		:param conn: AnaplanConnection object containing Workspace and Model ID, and AuthToken object
		:type conn: AnaplanConnection, optional
		:param results: JSON task results of an executed Anaplan action
		:type results: dict
		:param url: URL of the Anaplan action task
		:type url: str
		"""
		self._authorization = conn.get_auth().get_auth_token()
		Parser._results = Parser.parse_response(conn, results, url)

	@staticmethod
	def get_results() -> List[ParserResponse]:
		"""Get details of Anaplan action task

		:return: Friendly results of an executed task, including status, file and error dump if applicable
		:rtype: List[ParserResponse]
		"""
		return Parser._results

	@staticmethod
	def parse_response(conn: AnaplanConnection, results: dict, url: str):
		pass

	@staticmethod
	def failure_message(results: dict) -> ParserResponse:
		"""Creates a ParserResponse in case of an Action failure

		:return: Generic response for failed tasks.
		:rtype: ParserResponse
		"""
		if 'result' in results:
			if 'details' in results['result']:
				for i in range(0, len(results['result']['details'])):
					if 'localMessageText' in results['result']['details'][i]['localMessageText']:
						error_message = str(results['result']['details'][i]['localMessageText'])
						logger.error(f"The task has failed to run due to an error: {error_message}")
						return ParserResponse(f"The task has failed to run due to an error: {error_message}", "", False, pd.DataFrame())

	@staticmethod
	def get_dump(url: str) -> DataFrame:
		"""Fetches the failure dump of an Anaplan Import action if available

		:param url: URL of the Anaplan failure dump
		:type url: str
		:raises HTTPError: HTTP error code
		:raises ConnectionError: Network-related errors
		:raises SSLError: Server-side SSL certificate errors
		:raises Timeout: Request timeout errors
		:raises ConnectTimeout: Timeout error when attempting to connect
		:raises ReadTimeout: Timeout error waiting for server response
		:raises EmptyDataError: Error when data string is empty
		:raises ParserError: Source data in incorrect format
		:raises ParserWarning: Warning when parsing a file that doesn't use default parser
		:return: Failure dump for an import action
		:rtype: DataFrame
		"""
		authorization = Parser._authorization

		post_header = {
			'Authorization': authorization,
			'Content-Type': 'application/json'
		}

		edf = pd.DataFrame()
		dump = ""

		try:
			logger.debug("Fetching error dump")
			dump = requests.get(''.join([url, "/dump"]), headers=post_header, timeout=(5, 30)).text
			logger.debug("Error dump downloaded.")
		except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
			logger.error(f"Error fetching error dump {e}", exc_info=True)

		try:
			edf = pd.read_csv(StringIO(dump))
		except (EmptyDataError, ParserError) as e:
			logger.error(f"Error loading error dump to dataframe {e}", exc_info=True)
		except ParserWarning as w:
			logger.warning(f"Warning raised while parsing csv {w}", exc_info=True)

		return edf
