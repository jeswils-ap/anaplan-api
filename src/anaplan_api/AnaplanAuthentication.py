# ===============================================================================
# Created:			1 Nov 2021
# @author:			Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:		Abstract Anaplan Authentication Class
# Input:			Username & Password, or SHA keypair
# Output:			Anaplan JWT and token expiry time
# ===============================================================================
import json
import requests
import re
import logging
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from .AuthToken import AuthToken
from .util.Util import AuthenticationFailedError

logger = logging.getLogger(__name__)


class AnaplanAuthentication(object):

	def __init__(self):
		pass

	def auth_header(self, username: str, password: str):
		pass

	@staticmethod
	def auth_request(header: dict, body: str = None) -> str:
		"""
		:param header: Authorization header for request to auth server
		:param body: JSON body of auth request
		:return: JSON string with auth token details
		"""
		anaplan_url = 'https://auth.anaplan.com/token/authenticate'

		if body is None:
			logger.info("Authenticating via Basic.")
			try:
				authenticate = requests.post(anaplan_url, headers=header, timeout=(5, 30)).text
			except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
				logger.error(f"Error fetching auth token {e}", exc_info=True)
				raise Exception(f"Error fetching auth token {e}")
			except ValueError as e:
				logger.error(f"Error loading response JSON {e}", exc_info=True)
				raise ValueError(f"Error loading response JSON {e}")
		else:
			logger.info("Authenticating via Certificate.")
			try:
				authenticate = requests.post(anaplan_url, headers=header, data=json.dumps(body), timeout=(5, 30)).text
			except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
				logger.error(f"Error fetching auth token {e}", exc_info=True)
				raise Exception(f"Error fetching auth token {e}")
			except ValueError as e:
				logger.error(f"Error loading response JSON {e}", exc_info=True)
				raise ValueError(f"Error loading response JSON {e}")

		# Return the JSON array containing the authentication response, including AnaplanAuthToken
		return authenticate

	@staticmethod
	def authenticate(response: str) -> AuthToken:
		"""
		:param response: JSON string with auth request response.
		:return: List with auth token and expiry time
		"""
		try:
			json_response = json.loads(response)
		except ValueError as e:
			logger.error(f"Error loading response JSON {e}", exc_info=True)
			raise ValueError(f"Error loading JSON {response}")

		# Check that the request was successful, is so extract the AnaplanAuthToken value
		if 'status' in json_response:
			err_regex = re.compile('FAILURE.+')
			if not bool(re.match(err_regex, json_response['status'])):
				token = json_response['tokenInfo']['tokenValue']
				expires = json_response['tokenInfo']['expiresAt']
				status = AnaplanAuthentication.verify_auth(token)
				if status == 'Token validated':
					logger.info("User successfully authenticated.")
					return AuthToken(f"AnaplanAuthToken {token}", expires)
				else:
					logger.error(f"Error {status}")
					raise AuthenticationFailedError(f"Error getting authentication {status}")
			else:
				logger.error(f"Error {json_response['statusMessage']}")
				raise AuthenticationFailedError(f"Error logging in {json_response['statusMessage']}")

	@staticmethod
	def verify_auth(token: str) -> str:
		"""
		:param token: AnaplanAuthToken from authentication request.
		:return: JSON string with authentication validation.
		"""

		anaplan_url = "https://auth.anaplan.com/token/validate"
		header = {"Authorization": ''.join(["AnaplanAuthToken ", token])}

		try:
			logger.debug("Verifying auth token.")
			validate = json.loads(requests.get(anaplan_url, headers=header, timeout=(5, 30)).text)
		except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
			logger.error(f"Error verifying auth token {e}", exc_info=True)
			raise Exception(f"Error verifying auth token {e}")
		except ValueError as e:
			logger.error(f"Error loading response JSON {e}", exc_info=True)
			raise ValueError(f"Error loading response JSON {e}")

		if 'statusMessage' in validate:
			return validate['statusMessage']

	@staticmethod
	def refresh_token(token: str, auth_object: AuthToken):
		"""
		@param token: Token value that is nearing expiry
		@param auth_object: AuthToken object to be updated.
		"""
		new_token = ""
		new_expiry = ""

		url = "https://auth.anaplan.com/token/refresh"
		header = {"Authorization": ''.join(["AnaplanAuthToken ", token])}
		try:
			refresh = json.loads(requests.post(url, headers=header, timeout=(5, 30)).text)
		except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
			logger.error(f"Error verifying auth token {e}", exc_info=True)
			raise Exception(f"Error verifying auth token {e}")
		except ValueError as e:
			logger.error(f"Error loading response JSON {e}", exc_info=True)
			raise ValueError(f"Error loading response JSON {e}")
		
		if 'tokenInfo' in refresh:
			if 'tokenValue' in refresh['tokenInfo']:
				new_token = refresh['tokenInfo']['tokenValue']
			if 'expiresAt' in refresh['tokenInfo']:
				new_expiry = refresh['tokenInfo']['expiresAt']

		auth_object.set_auth_token(''.join(["AnaplanAuthToken ", new_token]))
		auth_object.set_token_expiry(new_expiry)
