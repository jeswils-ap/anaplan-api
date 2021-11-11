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
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from pandas.errors import EmptyDataError, ParserError
from .AnaplanConnection import AnaplanConnection
from .ParserResponse import ParserResponse

logger = logging.getLogger(__name__)


class Parser(object):
	_results: ParserResponse
	_authorization: str

	def __init__(self, conn: AnaplanConnection, results: dict, url: str):
		self._authorization = conn.get_auth().get_auth_token()
		Parser._results = Parser.parse_response(conn, results, url)

	@staticmethod
	def get_results():
		return Parser._results

	@staticmethod
	def parse_response(conn: AnaplanConnection, results: dict, url: str):
		pass

	@staticmethod
	def failure_message(results: dict):
		if 'result' in results:
			if 'details' in results['result']:
				for i in range(0, len(results['result']['details'])):
					if 'localMessageText' in results['result']['details'][i]['localMessageText']:
						error_message = str(results['result']['details'][i]['localMessageText'])
						logger.error(f"The task has failed to run due to an error: {error_message}")
						return ParserResponse(f"The task has failed to run due to an error: {error_message}", "", False, pd.DataFrame())

	@staticmethod
	def get_dump(url):
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
			logger.error(f"Error fetching error dump {e}")

		try:
			edf = pd.read_csv(StringIO(dump))
		except (EmptyDataError, ParserError) as e:
			logger.error(f"Error loading error dump to dataframe {e}")
		except ParserError as w:
			logger.warning(f"Warning raised while parsing csv {w}")

		return edf
