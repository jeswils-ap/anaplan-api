#===============================================================================
# Created:			1 Nov 2021
# @author:			Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:		Abstract Anaplan Authentication Class
# Input:			Username & Password, or SHA keypair
# Output:			Anaplan JWT and token expiry time
#===============================================================================
import json, logging, requests, re
from typing import List
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout

logger = logging.getLogger(__name__)

class AnaplanAuthentication(object):

	def __init__(self):
		pass

	def auth_header(self, username: str, password: str):
		pass

	@staticmethod
	def auth_request(header: dict, body: str = None) -> str:
		anaplan_url='https://auth.anaplan.com/token/authenticate'

		if body is None:
			logger.info("Authenticating via Basic.")
			authenticate = requests.post(anaplan_url, headers=header, timeout=(5,30)).text
		else:
			logger.info("Authenticating via Certificate.")
			authenticate = requests.post(anaplan_url, headers=header, data=json.dumps(body), timeout=(5,30)).text

		#Return the 	JSON array containing the authentication response, including AnaplanAuthToken
		return authenticate

	@staticmethod
	def authenticate(response: str) -> List[str]:
		try:
			json_response = json.loads(response)
		except ValueError as e:
			logger.error(f"Error loading response JSON {e}")

		#Check that the request was successful, is so extract the AnaplanAuthToken value 
		if 'status' in json_response:
			errReg = re.compile('FAILURE.+')
			if not bool(re.match(errReg, json_response['status'])):
				token = json_response['tokenInfo']['tokenValue']
				expires = json_response['tokenInfo']['expiresAt']
				status = AnaplanAuthentication.verify_auth(token)
				if status == 'Token validated':
					logger.info("User successfully authenticated.")
					return [f"AnaplanAuthToken {token}", expires]
				else:
					logger.error(f"Error {status}")
					return [None, None]
			else:
				logger.error(f"Error {json_response['statusMessage']}")

	@staticmethod
	def verify_auth(token: str) -> str:
		'''
		:param token: AnaplanAuthToken from authentication request.
		'''

		anaplan_url="https://auth.anaplan.com/token/validate"
		header = { "Authorization": ''.join(["AnaplanAuthToken ", token]) }

		try:
			logger.debug("Verifying auth token.")
			validate = json.loads(requests.get(anaplan_url, headers=header, timeout=(5,30)).text)
		except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
			logger.error(f"Error verifying auth token {e}")
		except ValueError as e:
			logger.error(f"Error loading response JSON {e}")

		if 'statusMessage' in validate:
			return validate['statusMessage']

	@staticmethod
	def refresh_token(token) -> List[str]:
		'''
		@param token: Token value that is nearing expiry 
		'''

		url="https://auth.anaplan.com/token/refresh"
		#header={ "Authorization" : "AnaplanAuthToken " + token }
		header = { "Authorization": ''.join(["AnaplanAuthToken ", token]) }
		try:
			refresh = json.loads(requests.post(url, headers=header, timeout=(5,30)).text)
		except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
			logger.error(f"Error verifying auth token {e}")
		except ValueError as e:
			logger.error(f"Error loading response JSON {e}")
		
		if 'tokenInfo' in refresh:
			if 'tokenValue' in refresh['tokenInfo']:
				new_token = refresh['tokenInfo']['tokenValue']
			if 'expiresAt' in refresh['tokenInfo']:
				new_expiry = refresh['tokenInfo']['expiresAt']

		return [''.join(["AnaplanAuthToken ", new_token]), new_expiry]