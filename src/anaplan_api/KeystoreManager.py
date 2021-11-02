#==============================================================================
# Created:		28 June 2018
# @author:		Jesse Wilson  (Anaplan Asia Pte Ltd)
# Description:	This class extracts the private key and public certificate 
#				from a Java Keystore and returns them as text.
# Input:		Java Keystore
# Output:		Key pair as array of strings
#==============================================================================
import jks, logging
from base64 import b64encode
from jks.util import BadKeystoreFormatException, UnsupportedKeystoreVersionException, KeystoreSignatureException, DuplicateAliasException, DecryptionFailureException, UnexpectedAlgorithmException

logger = logging.getLogger(__name__)


class KeystoreManager(object):
	path: str
	passphrase: str
	alias: str
	key_pass: str
	key: str
	cert: str

	def __init__(self, path, passphrase, alias, key_pass):
		self.path = path
		self.passphrase = passphrase
		self.alias = alias
		self.key_pass = key_pass

	def get_key(self):
		return self.key

	def get_cert(self):
		return self.cert

	#===============================================================================
	# This function fetches a key-pair from a Java keystore and prepares them for use
	#===============================================================================
	def get_keystore_pair(self):
		'''
		@param path: Local path to the Java keystore where the keypair(s) are stored
		@param passphrase: Passphrase required to extract the keys from the keystore
		@param alias: Name of the key-pair to be used
		@param key_pass: Password to decrypt the keystore
		'''
		
		PRIVATE_BEGIN = "-----BEGIN RSA PRIVATE KEY-----"
		PRIVATE_END = "-----END RSA PRIVATE KEY-----"
		PUBLIC_BEGIN = "-----BEGIN CERTIFICATE-----"
		PUBLIC_END = "-----END CERTIFICATE-----"

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
			logger.error(f"Upable to load keystore {e}")

		key = KeystoreManager.insert_newlines(b64encode(pk_entry.pkey_pkcs8).decode('utf-8'))
		cert = KeystoreManager.insert_newlines(b64encode(pk_entry.cert_chain[0][1]).decode('utf-8'))

		final_key = '\n'.join([PRIVATE_BEGIN, key, PRIVATE_END])
		final_cert = '\n'.join([PUBLIC_BEGIN, cert, PUBLIC_END])

		self.key = final_key.encode('utf-8')
		self.cert = final_cert

	#===========================================================================
	# This function converts base64 encoded private key and public certificate
	# strings and splits them into 64-character lines so they can be read and
	# handled correctly.
	#===========================================================================
	def insert_newlines(string, every=64):
		logger.debug("Formatting key text.")
		return '\n'.join(string[i:i+every] for i in range(0, len(string), every))
