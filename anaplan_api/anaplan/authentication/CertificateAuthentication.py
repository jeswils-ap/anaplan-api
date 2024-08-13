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
import re
import os
import logging
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from base64 import b64encode
from typing import Dict
from .AnaplanAuthentication import AnaplanAuthentication
from .CertificateHandler import CertificateHandler
from ..util.Util import InvalidKeyError

logger = logging.getLogger(__name__)


class CertificateAuthentication(AnaplanAuthentication):
    """
    Represents a certificate authentication request
    """

    required_params: set = {"private_key", "certificate"}

    # ===========================================================================
    # This function reads a user's public certificate as a string, base64
    # encodes that value, then returns the certificate authorization header.
    # ===========================================================================
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.certificate_details = CertificateHandler(**kwargs)

    def auth_header(self, certificate: str, **kwargs) -> Dict[str, str]:
        """Create the Auth API request header

        :param certificate: Path to public certificate or public certificate as a string
        :type certificate: str
        :return: Auth-API request authorization header
        :rtype: dict
        """

        """
        if not Path(certificate).is_file():
            my_pem_text = certificate
        else:
            with open(certificate, "r") as my_pem_file:
                my_pem_text = my_pem_file.read()

        if CertificateAuthentication._detect_certificate_format(my_pem_text) == "DER":
            my_pem_text = CertificateAuthentication._der_to_pem(my_pem_text.encode("utf-8")).decode("utf-8")"""

        header_string = {
            "Authorization": "".join(
                [
                    "CACertificate ",
                    b64encode(self.certificate_details.header.encode("utf-8")).decode("utf-8"),
                    # b64encode(my_pem_text.encode("utf-8")).decode("utf-8"),
                ]
            )
        }

        return header_string

    # ===========================================================================
    # This function takes a private key, calls the function to generate the nonce,
    # then the function to sign the nonce, and finally returns the Anaplan authentication
    # POST body value
    # ===========================================================================
    def generate_post_data(self, **kwargs) -> str:
        """Create the body of the Auth-API request

        :param private_key: Private key text or path to key
        :type private_key: bytes
        """

        """unsigned_nonce = CertificateAuthentication.create_nonce()
        signed_nonce = str(
            CertificateAuthentication.sign_string(unsigned_nonce, private_key)
        )

        json_string = "".join(
            [
                '{ "encodedData":"',
                str(b64encode(unsigned_nonce).decode("utf-8")),
                '", "encodedSignedData":"',
                signed_nonce,
                '"}',
            ]
        )"""

        return self.certificate_details.body

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
    def sign_string(message: bytes, private_key: bytes, key_password: bytes = b"") -> str:
        """Signs a string with a private key

        :param message: 150-character pseudo-random byte-array of characters
        :type message: bytes
        :param private_key: Private key text, used to sign the message.
        :type private_key: bytes
        :param key_password: Password for the private key, if it is encrypted.
        :type key_password: bytes
        :raises ValueError: Error loading the private or signing the message.
        :return: Base64 encoded signed string value
        :rtype: str
        """

        key_format = CertificateAuthentication._detect_key_format(private_key)

        if key_format == "":
            raise InvalidKeyError("Unable to determine the format of the supplied key.")

        key_encrypted = CertificateAuthentication._is_encrypted(private_key, key_format)

        if key_encrypted and key_password == b"":
            raise ValueError("Key password cannot be empty when the key is encrypted.")

        backend = default_backend()
        try:
            if key_format == "PEM":
                key = serialization.load_pem_private_key(
                    private_key, password=key_password, backend=backend
                )
            else:
                key = serialization.load_der_private_key(
                    private_key, password=key_password, backend=backend
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
