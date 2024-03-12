# ==============================================================================
# Created:		01 Nov 2021
# @author:		Jesse Wilson  (Anaplan Asia Pte Ltd)
# Description:	This class extracts the private key and public certificate
# 				from a Java Keystore and returns them as text.
# Input:		Java Keystore
# Output:		Key pair as array of strings
# ==============================================================================
from anaplan_api.pyjks.jks import jks
import logging
from base64 import b64encode
from anaplan_api.pyjks.jks import (
    BadKeystoreFormatException,
    UnsupportedKeystoreVersionException,
    KeystoreSignatureException,
    DuplicateAliasException,
    DecryptionFailureException,
    UnexpectedAlgorithmException,
)

logger = logging.getLogger(__name__)


class KeystoreManager(object):
    """
    Create a KeystoreManager object, which extracts and stores the public certificate and private key from a
    Java Keystore. It is initialized with the path to the Java Keystore, passphrase to open the keystore, alias of the
    desired key-pair, and the passphrase for the private key. At initialization, the certificate and private key are
    extracted and stored in the object.

    :param path: Path to the Java Keystore
    :type path: str
    :param passphrase: Passphrase to open the keystore
    :type passphrase: str
    :param alias: Alias of the desired key-pair in the store
    :type alias: str
    :param key_pass: Passphrase to read the private key
    :type key_pass: str
    :param _key: Byte array of the specified key in base64 format
    :type _key: bytes
    :param cert: String containing the certificate text in base64 format
    :type cert: str
    """

    path: str
    _passphrase: str
    alias: str
    _key_pass: str
    _key: bytes
    cert: str

    def __init__(self, path, passphrase, alias, key_pass):
        """
        :param path: Path to the Java Keystore
        :param passphrase: Passphrase to open the keystore
        :param alias: Alis of the desired key-pair in the store
        :param key_pass: Passphrase to read the private key.
        """
        self.path = path
        self._passphrase = passphrase
        self.alias = alias
        self._key_pass = key_pass

        self.get_keystore_pair()

    def get_key(self) -> bytes:
        """Get the private key

        :return: Content of the private key
        :rtype: bytes
        """
        return self._key

    def get_cert(self) -> str:
        """Get the public certificate

        :return: content of the public certificate
        :rtype: str
        """
        return self.cert

    # ===============================================================================
    # This function fetches a key-pair from a Java keystore and prepares them for use
    # ===============================================================================
    def get_keystore_pair(self):
        """Opens the keystore to read the specified key-pair. The strings are padded with the expected header
        and footer for RSA keys.

        :raises BadKeystoreFormatException: Structural error occurred while parsing the keystore
        :raises UnsupportedKeystoreVersionException: Unspecified or unsupported keystore version
        :raises KeystoreSignatureException: Specified password for keystore is invalid
        :raises DuplicateAliasException: Error if keystore contains duplicates of the specified alias
        :raises DecryptionFailureException: Error decrypting keystore entry
        :raises UnexpectedAlgorithmException: Unexpected cryptographic algorithm used in keystore
        """

        private_begin = "-----BEGIN RSA PRIVATE KEY-----"
        private_end = "-----END RSA PRIVATE KEY-----"
        public_begin = "-----BEGIN CERTIFICATE-----"
        public_end = "-----END CERTIFICATE-----"

        try:
            ks = jks.KeyStore.load(self.path, self._passphrase)
            logger.debug("Opening Java Keystore.")
            pk_entry = ks.private_keys[self.alias]
        except (
            BadKeystoreFormatException,
            UnsupportedKeystoreVersionException,
            KeystoreSignatureException,
            DuplicateAliasException,
        ) as e:
            logger.error(f"Error opening file {e}", exc_info=True)
            raise Exception(f"Error opening file {e}")

        try:
            if not pk_entry.is_decrypted():
                logger.debug("Decrypting keystore.")
                pk_entry.decrypt(self._key_pass)
            logger.debug("Keystore decrypted.")
        except (DecryptionFailureException, UnexpectedAlgorithmException) as e:
            logger.error(f"Unable to load keystore {e}", exc_info=True)
            raise Exception(f"Unable to load keystore {e}")

        key = KeystoreManager.insert_newlines(
            b64encode(pk_entry.pkey_pkcs8).decode("utf-8")
        )
        cert = KeystoreManager.insert_newlines(
            b64encode(pk_entry.cert_chain[0][1]).decode("utf-8")
        )

        final_key = "\n".join([private_begin, key, private_end])
        final_cert = "\n".join([public_begin, cert, public_end])

        self._key = final_key.encode("utf-8")
        self.cert = final_cert

    # ===========================================================================
    # This function converts base64 encoded private key and public certificate
    # strings and splits them into 64-character lines so that they can be read and
    # handled correctly.
    # ===========================================================================
    @staticmethod
    def insert_newlines(string: str, every=64) -> str:
        """Add newline character to string at `every` character marker and return a properly formatted PEM string.

        :param string: The content of a private key or public certificate
        :type string: str
        :param every: Number of character to insert a newline character
        :type every: int
        :return: Correctly format base64 PEM string.
        :rtype: str
        """
        logger.debug("Formatting key text.")
        return "\n".join(string[i : i + every] for i in range(0, len(string), every))
