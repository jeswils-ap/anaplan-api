# ==============================================================================
# Created:		01 Nov 2021
# @author:		Jesse Wilson  (Anaplan Asia Pte Ltd)
# Description:	This class extracts the private key and public certificate
# 				from a Java Keystore and returns them as text.
# Input:		Java Keystore
# Output:		Key pair as array of strings
# ==============================================================================
from anaplan_api import jks
import logging
from base64 import b64encode
from anaplan_api.jks.util import BadKeystoreFormatException, UnsupportedKeystoreVersionException, KeystoreSignatureException, \
	DuplicateAliasException, DecryptionFailureException, UnexpectedAlgorithmException

logger = logging.getLogger(__name__)


class KeystoreManager(object):
	path: str
	passphrase: str
	alias: str
	key_pass: str
	key: bytes
	cert: str

	def __init__(self, path, passphrase, alias, key_pass):
		self.path = path
		self.passphrase = passphrase
		self.alias = alias
		self.key_pass = key_pass

		self.get_keystore_pair()

	def get_key(self):
		return self.key

	def get_cert(self):
		return self.cert

	# ===============================================================================
	# This function fetches a key-pair from a Java keystore and prepares them for use
	# ===============================================================================
	def get_keystore_pair(self):

		private_begin = "-----BEGIN RSA PRIVATE KEY-----"
		private_end = "-----END RSA PRIVATE KEY-----"
		public_begin = "-----BEGIN CERTIFICATE-----"
		public_end = "-----END CERTIFICATE-----"

		try:
			ks = jks.KeyStore.load(self.path, self.passphrase)
			logger.debug("Opening Java Keystore.")
			pk_entry = ks.private_keys[self.alias]
		except (BadKeystoreFormatException, UnsupportedKeystoreVersionException, KeystoreSignatureException, DuplicateAliasException) as e:
			logger.error(f"Error opening file {e}")

		try:
			if not pk_entry.is_decrypted():
				logger.debug("Decrypting keystore.")
				pk_entry.decrypt(self.key_pass)
			logger.debug("Keystore decrypted.")
		except (DecryptionFailureException, UnexpectedAlgorithmException) as e:
			logger.error(f"Unable to load keystore {e}")

		key = KeystoreManager.insert_newlines(b64encode(pk_entry.pkey_pkcs8).decode('utf-8'))
		cert = KeystoreManager.insert_newlines(b64encode(pk_entry.cert_chain[0][1]).decode('utf-8'))

		final_key = '\n'.join([private_begin, key, private_end])
		final_cert = '\n'.join([public_begin, cert, public_end])

		self.key = final_key.encode('utf-8')
		self.cert = final_cert

	# ===========================================================================
	# This function converts base64 encoded private key and public certificate
	# strings and splits them into 64-character lines so they can be read and
	# handled correctly.
	# ===========================================================================
	@staticmethod
	def insert_newlines(string, every=64):
		logger.debug("Formatting key text.")
		return '\n'.join(string[i:i+every] for i in range(0, len(string), every))
