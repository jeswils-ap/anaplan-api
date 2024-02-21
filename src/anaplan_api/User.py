import json
import logging
import requests
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from .AnaplanConnection import AnaplanConnection
from .util.AnaplanVersion import AnaplanVersion
from .UserDetails import UserDetails

logger = logging.getLogger(__name__)


class User:
	"""
	Class representing an Anaplan user
	"""
	_url: str = f"https://api.anaplan.com/{AnaplanVersion().major}/{AnaplanVersion().minor}/users/"
	_conn: AnaplanConnection
	_user_id: str
	_user_details: UserDetails

	def __init__(self, conn: AnaplanConnection, user_id: str = None):
		"""
		:param conn: Object containing Workspace and Model ID, and AuthToken object
		:type conn: AnaplanConnection
		:param user_id: ID of specified user
		:type user_id: str
		"""
		self._conn = conn
		self._user_id = user_id

	def get_current_user(self):
		"""Get the ID of the current user

		:raises HTTPError: HTTP error code
		:raises ConnectionError: Network-related errors
		:raises SSLError: Server-side SSL certificate errors
		:raises Timeout: Request timeout errors
		:raises ConnectTimeout: Timeout error when attempting to connect
		:raises ReadTimeout: Timeout error waiting for server response
		:raises ValueError: Error loading text response to JSON
		:raises KeyError: Error locating User or ID key in JSON response.
		"""
		if self._user_id is None:
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
				raise Exception(f"Error fetching user details {e}")
			except ValueError as e:
				logger.error(f"Error loading user details {e}", exc_info=True)
				raise ValueError(f"Error loading user details {e}")

			if 'user' in user_details:
				if 'id' in user_details['user']:
					self._user_id = user_details['user']['id']
					self._user_details = UserDetails(user_details['user'])
				else:
					raise KeyError("'id' not found in response")
			else:
				raise KeyError("'user' not found in response")

	def get_user_details(self):
		"""Get details of the specified user

		:raises HTTPError: HTTP error code
		:raises ConnectionError: Network-related errors
		:raises SSLError: Server-side SSL certificate errors
		:raises Timeout: Request timeout errors
		:raises ConnectTimeout: Timeout error when attempting to connect
		:raises ReadTimeout: Timeout error waiting for server response
		:raises ValueError: Error loading text response to JSON
		:raises KeyError: Error locating User or ID key in JSON response.
		"""
		if self._user_id is not None:
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
				raise Exception(f"Error fetching user details {e}")
			except ValueError as e:
				logger.error(f"Error loading user details {e}", exc_info=True)
				raise ValueError(f"Error loading user details {e}")

			if 'user' in user_details:
				if 'id' in user_details['user']:
					self._user_id = user_details['user']['id']
					self._user_details = UserDetails(user_details['user'])
				else:
					raise KeyError("'id' not found in response")
			else:
				raise KeyError("'user' not found in response")

	def get_conn(self) -> AnaplanConnection:
		"""Get AnaplanConnection object

		:return: AnaplanConnection object for current user
		:rtype: AnaplanConnection
		"""
		return self._conn

	def get_url(self) -> str:
		"""Get base URL for user requests

		:return: User details url
		:rtype: str
		"""
		return self._url

	def get_id(self) -> str:
		"""Get ID of the specified user

		:return: User ID
		:rtype: str
		"""
		return self._user_id

	def get_user(self) -> UserDetails:
		"""Get details for the specified user

		:return: Friendly user details
		:rtype: UserDetails
		"""
		return self._user_details

	def get_models(self):
		"""Get list of models for a user"""

	def get_workspace(self):
		"""Get list of workspaces for a user"""
