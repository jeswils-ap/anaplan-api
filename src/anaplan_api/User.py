import json
import logging
import requests
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from .AnaplanConnection import AnaplanConnection
from .util.AnaplanVerion import AnaplanVersion
from .UserDetails import UserDetails

logger = logging.getLogger(__name__)


class User:
	_url: str = f"https://api.anaplan.com/{AnaplanVersion.major()}/{AnaplanVersion.minor()}/users/"
	_conn: AnaplanConnection
	_user_id: str
	_user_details: UserDetails

	def __init__(self, conn: AnaplanConnection, user_id: str = None):
		self._conn = conn
		self._user_id = user_id

	def get_current_user(self) -> None:
		if self._user_id is None:
			user_details = {}
			url = ''.join([self._url, "me"])
			authorization = self._conn.get_auth().get_auth_token()

			get_header = {
				"Authorization": authorization
			}

			logger.debug("Fetching user ID.")

			try:
				logger.debug("Retrieving details of current user.")
				user_details = json.loads(requests.get(url, headers=get_header, timeout=(5, 30)).text)
			except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
				logger.error(f"Error fetching user details {e}", exc_info=True)
			except ValueError as e:
				logger.error(f"Error loading model list {e}", exc_info=True)

			if 'user' in user_details:
				if 'id' in user_details['user']:
					self._user_id = user_details['user']['id']
					self._user_details = UserDetails(user_details['user'])
				else:
					raise KeyError("'id' not found in response")
			else:
				raise KeyError("'user' not found in response")

	def get_user_details(self) -> None:
		if self._user_id is not None:
			user_details = {}
			url = ''.join([self._url, self._user_id])
			authorization = self._conn.get_auth().get_auth_token

			get_header = {
				"Authorization": authorization
			}

			logger.debug("Fetching user ID.")

			try:
				logger.debug("Retrieving details of current user.")
				user_details = json.loads(requests.get(url, headers=get_header, timeout=(5, 30)).text)
			except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
				logger.error(f"Error fetching user details {e}", exc_info=True)
			except ValueError as e:
				logger.error(f"Error loading model list {e}", exc_info=True)

			if 'user' in user_details:
				if 'id' in user_details['user']:
					self._user_id = user_details['user']['id']
					self._user_details = UserDetails(user_details['user'])
				else:
					raise KeyError("'id' not found in response")
			else:
				raise KeyError("'user' not found in response")

	def get_conn(self) -> AnaplanConnection:
		return self._conn

	def get_url(self) -> str:
		return self._url

	def get_id(self) -> str:
		return self._user_id

	def get_user(self) -> UserDetails:
		return self._user_details

	def get_models(self):
		"""Get list of models for a user"""

	def get_workspace(self):
		"""Get list of workspaces for a user"""
