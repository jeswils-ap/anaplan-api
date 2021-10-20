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

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from base64 import b64encode
import requests
import json
import os
import jks
import logging

logger = logging.getLogger(__name__)

#===========================================================================
# This function sets the log level for the library.
#===========================================================================
def create_logger(level):
	'''
    :param level: Log level to report
    :param *args: If not null, path to file save logs.
    '''
	logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=level)
	global logger
	logger = logging.getLogger("AnaplanPythonAPI")


#===========================================================================
# This function reads a pseudo-randomly generated nonce and signs the text
# with the private key.
#===========================================================================
def sign_string(message, privKey):
	'''
	:param message: 150-character psuedo-random byte-array of characters
	:param privKey: Private key text, used to since the message. 
	'''
	
	backend = default_backend()
	try:
		key = serialization.load_pem_private_key(privKey, None, backend=backend)
	except ValueError as e:
		logger.error("Error loading private key %s", e)
	try:	
		signature = key.sign(message, padding.PKCS1v15(), hashes.SHA512())
		return b64encode(signature).decode('utf-8')
	except ValueError as e:
		logger.error("Error signing message %s", e)

#===========================================================================
# The function generates a pseudo-random alpha-numeric 150 character nonce
# and returns the value
#===========================================================================
def create_nonce():
	randArr = os.urandom(150)
	
	return randArr
	
#===========================================================================
# This function takes a private key, calls the function to generate the nonce,
# then the function to sign the nonce, and finally returns the Anaplan authentication
# POST body value
#===========================================================================	
def generate_post_data(privKey):
	'''
	:param privKey: Path to private key
	'''
	
	unsigned_nonce=create_nonce()
	signed_nonce=str(sign_string(unsigned_nonce, privKey))
	
	json_string='{ "encodedData":"' + str(b64encode(unsigned_nonce).decode('utf-8')) + '", "encodedSignedData":"' + signed_nonce + '"}'

	return json_string

#===========================================================================
# This function reads a user's public certificate as a string, base64 
# encodes that value, then returns the certificate authorization header.
#===========================================================================
def certificate_auth_header(pubCert):
	'''
	:param pubCert: Path to public certificate
	'''
	
	if(pubCert[:5] == "-----"):
		my_pem_text=pubCert
	else:
		with open(pubCert, "r") as my_pem_file:
			my_pem_text = my_pem_file.read()
		
	#pem_content = my_pem_text.replace("\n", "").replace("-----BEGIN CERTIFICATE-----", "").replace("-----END CERTIFICATE-----", "")	
	#header_string = { 'AUTHORIZATION':'CACertificate ' + b64encode(pem_content.encode('utf-8')).decode('utf-8') }
	
	header_string = { 'AUTHORIZATION' : 'CACertificate ' + b64encode(my_pem_text.encode('utf-8')).decode('utf-8') }
	
	return header_string

#===========================================================================
# This function takes in the Anaplan username and password, base64 encodes
# them, then returns the basic authorization header.
#===========================================================================
def basic_auth_header(username, password):
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
def auth_request(header, body):	
	'''
	:param header: Authorization type, CACertificate or Basic
	:param body: POST request body: encodedData (150-character nonce), encodedSignedData (encodedData value signed by private key)
	'''
	
	anaplan_url='https://auth.anaplan.com/token/authenticate'
	
	if body == None:
		logger.info("Authenticating via Basic.")
		r=requests.post(anaplan_url, headers=header)
	else:	
		logger.info("Authenticating via Certificate.")
		r=requests.post(anaplan_url, headers=header, data=json.dumps(body))

	#Return the 	JSON array containing the authentication response, including AnaplanAuthToken
	return r.text

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
# This function reads the string value of the JSON response for the Anaplan
# authentication request. If the login was successful, it verifies the token,
# then returns the Authorization header for the API. If unsuccessful, it returns
# the error message.
#===========================================================================
def authenticate(response):	
	'''
	:param response: JSON array of authentication request
	'''
	
	json_response = json.loads(response)
	#Check that the request was successful, is so extract the AnaplanAuthToken value 
	if not json_response["status"] == "FAILURE_BAD_CREDENTIAL":
		token = json_response["tokenInfo"]["tokenValue"]
		status = verify_auth(token)
		if status == 'Token validated':
			logger.info("User successfully authenticated.")
			return "AnaplanAuthToken " + token
		else:
			logger.error("Error %s", status)
	else:
		logger.error("Error %s", json_response["statusMessage"])

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