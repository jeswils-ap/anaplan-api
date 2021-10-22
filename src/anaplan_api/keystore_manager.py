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

logger = logging.getLogger(__name__)

#===============================================================================
# This function fetches a key-pair from a Java keystore and prepares them for use
#===============================================================================
def get_keystore_pair(path, passphrase, alias, key_pass):
	'''
	@param path: Local path to the Java keystore where the keypair(s) are stored
	@param passphrase: Passphrase required to extract the keys from the keystore
	@param alias: Name of the key-pair to be used
	@param key_pass: Password to decrypt the keystore
	'''
	
	PRIVATE_BEGIN="-----BEGIN RSA PRIVATE KEY-----"
	PRIVATE_END="-----END RSA PRIVATE KEY-----"
	PUBLIC_BEGIN="-----BEGIN CERTIFICATE-----"
	PUBLIC_END="-----END CERTIFICATE-----"

	try:
		ks=jks.KeyStore.load(path, passphrase)
		logger.debug("Opening Java Keystore.")
		pk_entry=ks.private_keys[alias]
	except Exception as e:
		logger.error("Error opening file %s", e)

	try:
		if not pk_entry.is_decrypted():
			logger.debug("Decrypting keystore.")
			pk_entry.decrypt(key_pass)
		logger.debug("Keystore decrypted.")
	except Exception as e:
		logger.error("Upable to load keystore %s", e)

	key=insert_newlines(b64encode(pk_entry.pkey_pkcs8).decode('utf-8'))
	cert=insert_newlines(b64encode(pk_entry.cert_chain[0][1]).decode('utf-8'))

	final_key='\n'.join([PRIVATE_BEGIN, key, PRIVATE_END])
	final_cert='\n'.join([PUBLIC_BEGIN, cert, PUBLIC_END])

	return final_key.encode('utf-8'), final_cert

#===========================================================================
# This function converts base64 encoded private key and public certificate
# strings and splits them into 64-character lines so they can be read and
# handled correctly.
#===========================================================================
def insert_newlines(string, every=64):
	logger.debug("Formatting key text.")
	return '\n'.join(string[i:i+every] for i in range(0, len(string), every))