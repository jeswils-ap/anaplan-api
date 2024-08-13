from typing import Optional

import re
import os
from base64 import b64encode
import logging

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

from pyasn1.codec.der import decoder
from pyasn1_modules import rfc7292

from ..util.Util import InvalidKeyError

logger = logging.getLogger(__name__)


class CertificateHandler:
    """
    Handler for S/MIME certificates for Anaplan authentication
    """
    def __init__(self, certificate: bytes, private_key: Optional[bytes] = None, password: Optional[bytes] = None):
        self.certificate = certificate
        self.private_key = private_key
        self.password = password

        if self.check_pfx():
            self.load_pfx()
        else:
            self.key_format = self._detect_key_format()
            self.certificate_format = self._detect_certificate_format()
            if self.certificate_format == "":
                raise InvalidKeyError("Unable to determine the format of the supplied certificate.")

            self.encrypted = self._is_encrypted()
            if self.encrypted and self.password == b"":
                raise ValueError("Key password cannot be empty when the key is encrypted.")

            self.header = self.encode_public_certificate()
            self.body = self.generate_post_data()

    def check_pfx(self) -> bool:
        """Check if the certificate is in PFX format
        :return: True if the certificate matches PFX format
        :rtype: bool
        """
        logger.debug("Checking if a PFX file was provided.")
        try:
            pfx, _ = decoder.decode(
                self.certificate,
                asn1Spec=rfc7292.PFX()
            )
            return True
        except Exception:
            pass

        return False

    def _detect_key_format(self) -> str:
        """Detect the format of the private key to ensure the correct serialisation is used

        :return: Format of the supplied key
        :rtype: str
        """
        key_formats: dict[str, bytes] = {
            "PEM": b"^-----BEGIN (.*)-----",
            "DER": b"^(0\\x82)"
        }
        logger.debug("Verifying private key format")
        for key_format, search in key_formats.items():
            if re.search(search, self.private_key):
                logger.debug(f"Private key format: {key_format}")
                return key_format
        return ""

    def load_pfx(self):
        """Load the private key and certificate from a PFX file

        :raises ValueError: Error when attempting to load the PFX file
        """
        logger.debug("Loading private key and certificate from supplied PFX")
        try:
            self.certificate = pkcs12.load_key_and_certificates(
                self.certificate,
                password=self.password,
                backend=default_backend()
            )
        except ValueError as e:
            logger.error(f"Error loading PFX: {e}", exc_info=True)
            raise ValueError(f"Error loading PFX: {e}")

    def encode_public_certificate(self) -> str:
        """Create the Auth API request header

        :return: Auth-API request authorization header
        :rtype: dict
        """
        my_pem_text = self.certificate

        if self.certificate_format == "DER":
            my_pem_text = CertificateHandler._der_to_pem(self.certificate)

        return b64encode(my_pem_text).decode("utf-8")

    @staticmethod
    def _der_to_pem(der_data: bytes) -> bytes:
        """Convert DER-encoded public certificate to PEM for use in Anaplan Auth Header

        :param der_data: DER-encoded file data
        :type der_data: bytes
        return: PEM encoded public certificate
        :rtype: bytes
        """
        try:
            logger.debug("Converting DER-encoded public certificate to PEM")
            certificate = x509.load_der_x509_certificate(der_data, default_backend())
            pem_data = certificate.public_bytes(
                encoding=serialization.Encoding.PEM
            )
            return pem_data
        except ValueError as e:
            logger.error(f"Error decoding certificate: {e}", exc_info=True)
            raise ValueError(f"Error decoding certificate: {e}")

    def _detect_certificate_format(self) -> str:
        """Check the format of the certificate for PEM or DER encoding.

        :return: Format of the supplied certificate
        :rtype: str
        """
        key_formats: dict[str, bytes] = {
            "PEM": b"^-----BEGIN (.*)-----",
            "DER": b"^(0\\x82|0\\x84)"
        }

        logger.debug("Verifying certificate format.")
        for key_format, search in key_formats.items():
            if re.search(search, self.certificate):
                logger.debug(f"Certificate format: {key_format}")
                return key_format

        return ""

    def _is_encrypted(self) -> bool:
        """Check if the private key is encrypted

        :return: True if encrypted, False otherwise
        :rtype: bool
        :raises: ValueError
        """
        if self.certificate_format == "PEM":
            return re.search(b"^-----BEGIN ENCRYPTED PRIVATE KEY-----", self.private_key) is not None
        if self.certificate_format == "DER":
            try:
                key = serialization.load_der_private_key(
                    self.private_key,
                    password=None,
                    backend=default_backend()
                )
                return True
            except Exception:
                return False
        raise ValueError("Unable to determine if the supplied key is encrypted.")

    # ===========================================================================
    # This function takes a private key, calls the function to generate the nonce,
    # then the function to sign the nonce, and finally returns the Anaplan authentication
    # POST body value
    # ===========================================================================
    def generate_post_data(self) -> str:
        """Create the body of the Auth-API request

        :return:
        """

        unsigned_nonce = CertificateHandler.create_nonce()
        signed_nonce = str(
            self.sign_string(unsigned_nonce)
        )

        json_string = "".join(
            [
                '{ "encodedData":"',
                str(b64encode(unsigned_nonce).decode("utf-8")),
                '", "encodedSignedData":"',
                signed_nonce,
                '"}',
            ]
        )

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
    def sign_string(self, message: bytes) -> str:
        """Signs a string with a private key

        :param message: 150-character pseudo-random byte-array of characters
        :type message: bytes
        :raises ValueError: Error loading the private or signing the message.
        :return: Base64 encoded signed string value
        :rtype: str
        """

        backend = default_backend()
        try:
            if self.key_format == "PEM":
                key = serialization.load_pem_private_key(
                    self.private_key, password=self.password, backend=backend
                )
            else:
                key = serialization.load_der_private_key(
                    self.private_key, password=self.password, backend=backend
                )
            try:
                signature = key.sign(message, padding.PKCS1v15(), hashes.SHA512())
                return b64encode(signature).decode("utf-8")
            except ValueError as e:
                logger.error(f"Error signing message {e}", exc_info=True)
                raise ValueError(f"Error signing message {e}")
        except ValueError as e:
            logger.error(f"Error loading private key {e}", exc_info=True)
            raise ValueError(f"Error loading private key {e}")
