# ==============================================================================
# Created:		28 June 2018
# @author:		Jesse Wilson  (Anaplan Asia Pte Ltd)
# Description:	This script reads a user's public and private keys in order to
# 				sign a cryptographic nonce. It then generates a request to
# 				authenticate with Anaplan, passing the signed and unsigned
# 				nonce in the body of the request.
# Input:		Public certificate file location, private key file location
# Output:		Authorization header string, request body string containing a nonce and its signed value
# ==============================================================================
import os
import logging
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from base64 import b64encode
from typing import Dict
from .AnaplanAuthentication import AnaplanAuthentication

logger = logging.getLogger(__name__)


class CertificateAuthentication(AnaplanAuthentication):
	"""
	Represents a certificate authentication request
	"""
	# ===========================================================================
	# This function reads a user's public certificate as a string, base64
	# encodes that value, then returns the certificate authorization header.
	# ===========================================================================
	def auth_header(self, pub_cert: str, **kwargs) -> Dict[str, str]:
		"""Create the Auth API request header

		:param pub_cert: Path to public certificate or public certificate as a string
		:type pub_cert: str
		:return: Auth-API request authorization header
		:rtype: dict
		"""

		if not os.path.isfile(pub_cert):
			my_pem_text = pub_cert
		else:
			with open(pub_cert, "r") as my_pem_file:
				my_pem_text = my_pem_file.read()

		header_string = {'Authorization': ''.join(['CACertificate ', b64encode(my_pem_text.encode('utf-8')).decode('utf-8')])}

		return header_string

	# ===========================================================================
	# This function takes a private key, calls the function to generate the nonce,
	# then the function to sign the nonce, and finally returns the Anaplan authentication
	# POST body value
	# ===========================================================================
	@staticmethod
	def generate_post_data(priv_key: bytes) -> str:
		"""Create the body of the Auth-API request

		:param priv_key: Private key text or path to key
		:type priv_key: bytes
		"""

		unsigned_nonce = CertificateAuthentication.create_nonce()
		signed_nonce = str(CertificateAuthentication.sign_string(unsigned_nonce, priv_key))

		json_string = ''.join(['{ "encodedData":"', str(b64encode(unsigned_nonce).decode('utf-8')), '", "encodedSignedData":"', signed_nonce, '"}'])

		return json_string

	# ===========================================================================
	# The function generates a pseudo-random alpha-numeric 150 character nonce
	# and returns the value
	# ===========================================================================
	@staticmethod
	def create_nonce() -> bytes:
		"""Create a random 150-character byte array

		:return: Bytes object containing 150 characters
		:rtype: bytes
		"""
		rand_arr = os.urandom(150)

		return rand_arr

	# ===========================================================================
	# This function reads a pseudo-randomly generated nonce and signs the text
	# with the private key.
	# ===========================================================================
	@staticmethod
	def sign_string(message: bytes, priv_key: bytes) -> str:
		"""Signs a string with a private key

		:param message: 150-character pseudo-random byte-array of characters
		:type message: bytes
		:param priv_key: Private key text, used to sign the message.
		:type priv_key: bytes
		:raises ValueError: Error loading the private or signing the message.
		:return: Base64 encoded signed string value
		:rtype: str
		"""

		backend = default_backend()
		try:
			if not os.path.isfile(priv_key):
				key = serialization.load_pem_private_key(priv_key, None, backend=backend)
			else:
				with open(priv_key, 'r') as key_file:
					serialization.load_pem_private_key(open(priv_key, 'r').read().encode('utf-8'), None, backend=backend)
			try:
				signature = key.sign(message, padding.PKCS1v15(), hashes.SHA512())
				return b64encode(signature).decode('utf-8')
			except ValueError as e:
				logger.error(f"Error signing message {e}", exc_info=True)
				raise ValueError(f"Error signing message {e}")
		except ValueError as e:
			logger.error(f"Error loading private key {e}", exc_info=True)
			raise ValueError(f"Error loading private key {e}")
