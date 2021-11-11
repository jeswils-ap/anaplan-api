from typing import Union
from .BasicAuthentication import BasicAuthentication
from .CertificateAuthentication import CertificateAuthentication
from .util.Util import InvalidAuthenticationError


class AuthFactory:
	"""Class responsible for handling auth type logic and returning the correct authentication generator"""

	_auths: dict = {
		"basic": BasicAuthentication,
		"certificate": CertificateAuthentication
	}

	_auth_type: str

	def __init__(self, auth_type):
		if auth_type in self._auth_type:
			self._auth_type = auth_type.lower()
		else:
			raise InvalidAuthenticationError(f"Invalid authentication option, expected types are "
									f"{''.join(list(self._auths.keys()))}")

	def get_auth(self) -> Union[BasicAuthentication, CertificateAuthentication]:
		return self._auths[self._auth_type]
