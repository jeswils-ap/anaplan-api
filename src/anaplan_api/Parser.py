#===============================================================================
# Created:			29 Oct 2021
# @author:			Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:		Generic class to parse Anaplan API task responses
# Input:			JSON array of task results, URL of Anaplan task, Task ID string,
#					Request header string
# Output:			Array containing overall task results string, details results string,
#					error dump dataframe.
#===============================================================================
import logging, requests
import pandas as pd
from io import StringIO
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from pandas.errors import EmptyDataError, ParserError, ParserWarning
from anaplan_api.AnaplanConnection import AnaplanConnection


logger = logging.getLogger(__name__)


class Parser(object):
	results = []
	authorization: str

	def __init__(self, conn: AnaplanConnection, results: dict, url: str):
		self.authorization = conn.get_auth()
		Parser.results = Parser.parse_response(conn, results, url)

	@staticmethod
	def get_results():
		return Parser.results

	def parse_response(self):
		pass

	@staticmethod
	def failure_message(self, results: dict):
		if 'result' in results:
				if 'details' in results['result']:
					for i in range(0, len(results['result']['details'])):
						if 'localMessageText' in results['result']['details'][i]['localMessageText']:
							error_message = str(results['result']['details'][i]['localMessageText'])
							logger.error(f"The task has failed to run due to an error: {error_message}")
							return (f"The task has failed to run due to an error: {error_message}", None)

	@staticmethod
	def get_dump(url):
		authorization = self.authorization

		post_header = {
						'Authorization': authorization,
						'Content-Type': 'application/json'
				}

		eDf = pd.DataFrame()

		try:
			logger.debug("Fetching error dump")
			dump = requests.get(''.join([url, "/dump"]), headers=post_header, timeout=(5,30)).text
			logger.debug("Error dump downloaded.")
		except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
			logger.error(f"Error fetching error dump {e}")

		try:
			eDf = pd.read_csv(StringIO(dump))
		except EmptyDataError, ParserError as e:
			logger.error(f"Error loading error dump to dataframe {e}")
		except ParserError as w:
			logger.warning(f"Wanring raised while parsing csv {e}")

		return eDf
