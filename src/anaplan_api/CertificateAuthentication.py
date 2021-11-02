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
import os, logging
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from base64 import b64encode
from typing import List
from anaplan_api.AnaplanAuthentication import AnaplanAuthentication

logger = logging.getLogger(__name__)

class CertificateAuthentication(AnaplanAuthentication):
	#===========================================================================
	# This function reads a user's public certificate as a string, base64 
	# encodes that value, then returns the certificate authorization header.
	#===========================================================================
	def auth_header(self, pubCert) -> str:
		'''
		:param pubCert: Path to public certificate
		'''

		if(pubCert[:5] == "-----"):
			my_pem_text=pubCert
		else:
			with open(pubCert, "r") as my_pem_file:
				my_pem_text = my_pem_file.read()

		#header_string = { 'AUTHORIZATION' : 'CACertificate ' + b64encode(my_pem_text.encode('utf-8')).decode('utf-8') }
		header_string = { 'AUTHORIZATION' : ''.join(['CACertificate ', b64encode(my_pem_text.encode('utf-8')).decode('utf-8')])}

		return header_string

	#===========================================================================
	# This function takes a private key, calls the function to generate the nonce,
	# then the function to sign the nonce, and finally returns the Anaplan authentication
	# POST body value
	#===========================================================================	
	def generate_post_data(self, privKey) -> str:
		'''
		:param privKey: Path to private key
		'''

		unsigned_nonce = CertificateAuthentication.create_nonce()
		signed_nonce=str(CertificateAuthentication.sign_string(unsigned_nonce, privKey))

		#json_string='{ "encodedData":"' + str(b64encode(unsigned_nonce).decode('utf-8')) + '", "encodedSignedData":"' + signed_nonce + '"}'
		json_string = ''.join(['{ "encodedData":"', str(b64encode(unsigned_nonce).decode('utf-8')), '", "encodedSignedData":"', signed_nonce, '"}'])

		return json_string

	#===========================================================================
	# The function generates a pseudo-random alpha-numeric 150 character nonce
	# and returns the value
	#===========================================================================
	@staticmethod
	def create_nonce() -> str:
		randArr = os.urandom(150)

		return randArr

	#===========================================================================
	# This function reads a pseudo-randomly generated nonce and signs the text
	# with the private key.
	#===========================================================================
	@staticmethod
	def sign_string(message, privKey) -> str:
		'''
		:param message: 150-character psuedo-random byte-array of characters
		:param privKey: Private key text, used to since the message.
		:returns: B64 encoded signed nonce
		'''

		backend = default_backend()
		try:
			key = serialization.load_pem_private_key(privKey, None, backend=backend)
		except ValueError as e:
			logger.error(f"Error loading private key {e}")
		try:	
			signature = key.sign(message, padding.PKCS1v15(), hashes.SHA512())
			return b64encode(signature).decode('utf-8')
		except ValueError as e:
			logger.error(f"Error signing message {e}")
