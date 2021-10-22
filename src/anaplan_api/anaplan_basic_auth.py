#==============================================================================
# Created:		28 June 2018
# @author:		Jesse Wilson  (Anaplan Asia Pte Ltd)
# Description:	This script reads a user's public and private keys in order to
# 				sign a cryptographic nonce. It then generates a request to
# 				authenticate with Anaplan, passing the signed and unsigned
# 				nonces in the body of the request.
# Input:			Public certificate file location, private key file location
# Output:		Authorization header string, request body string containing a nonce and its signed value
#==============================================================================

from requests.exceptions import HTTPError
from base64 import b64encode
import requests
import json
import logging

logger = logging.getLogger(__name__)

#===========================================================================
# This function takes in the Anaplan username and password, base64 encodes
# them, then returns the basic authorization header.
#===========================================================================
def auth_header(username, password):
	'''
	:param username: Anaplan username
	:param password: Anaplan password
	'''
	
	header_string = { 'Authorization':'Basic ' + b64encode((username + ":" + password).encode('utf-8')).decode('utf-8') }
	return header_string

#===========================================================================
# This function takes the provided authorization header and POST body (if applicable),
# sends the authentication request to Anaplan, and returns the response as a string.
#===========================================================================
def auth_request(header):	
	'''
	:param header: Authorization type, CACertificate or Basic
	:param body: POST request body: encodedData (150-character nonce), encodedSignedData (encodedData value signed by private key)
	'''
	
	anaplan_url='https://auth.anaplan.com/token/authenticate'
	
	try:
		logger.info("Authenticating via Basic.")
		r=requests.post(anaplan_url, headers=header)
	except HTTPError as e:
		logger.error("Error authenticating via Basic {0}".format(e))
		raise HTTPError(e)

	#Return the 	JSON array containing the authentication response, including AnaplanAuthToken
	return r.text

#===========================================================================
# This function reads the string value of the JSON response for the Anaplan
# authentication request. If the login was successful, it verifies the token,
# then returns the Authorization header for the API. If unsuccessful, it returns
# the error message.
#===========================================================================
def authenticate(response):	
	'''
	:param response: JSON array of authentication request
	:returns: Header Authenication value, and token expiry in epoch
	'''
	
	json_response = json.loads(response)
	#Check that the request was successful, is so extract the AnaplanAuthToken value 
	if not json_response["status"] == "FAILURE_BAD_CREDENTIAL":
		token = json_response["tokenInfo"]["tokenValue"]
		expires = json_response["tokenInfo"]["expiresAs"]
		status = verify_auth(token)
		if status == 'Token validated':
			logger.info("User successfully authenticated.")
			return "AnaplanAuthToken {0}".format(token), expires
		else:
			logger.error("Error %s", status)
	else:
		logger.error("Error %s", json_response["statusMessage"])

#===========================================================================
# This function reads the Anaplan auth token value and verifies its validity.
#===========================================================================
def verify_auth(token):	
	'''
	:param token: AnaplanAuthToken from authentication request.
	'''
	
	anaplan_url="https://auth.anaplan.com/token/validate"
	header = { "Authorization": "AnaplanAuthToken " + token }
	
	try:
		logger.debug("Verifying auth token.")
		r=requests.get(anaplan_url, headers=header)
	except ValueError as e:
		logger.error("Error verifying auth token %s", e)
	
	status=json.loads(r.text)
	
	return status["statusMessage"]

#===========================================================================
# This function takes in the current token value, refreshes, and returns the
# updated token Authorization header value.
#===========================================================================
def refresh_token(token):	
	'''
	@param token: Token value that is nearing expiry 
	'''
	
	url="https://auth.anaplan.com/token/refresh"
	header={ "Authorization" : "AnaplanAuthToken " + token }
	r = requests.post(url, headers=header)
	
	new_token=json.loads(r.text)["tokenInfo"]["tokenValue"]
	
	return "AnaplanAuthToken " + new_token