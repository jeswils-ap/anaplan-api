import logging
import requests
from time import time
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from anaplan_api.util.Util import InvalidTokenError, RequestFailedError
from anaplan_api import AnaplanConnection
from anaplan_api import AnaplanRequest

logger = logging.getLogger(__name__)


class AnaplanSession:
	_session: requests.sessions.Session
	_conn: AnaplanConnection

	def __init__(self, conn: AnaplanConnection):
		self._session = requests.Session()
		self._conn = conn

	def __enter__(self):
		self._session.headers.update({'Authorization': self._conn.get_auth().get_auth_token()})
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self._session.close()

	@staticmethod
	def check_expired(expiry: float):
		return expiry - (10 * 60) > time()

	def get(self, req: AnaplanRequest):
		expiry: float
		result: requests.Response

		try:
			expiry = self._conn.get_auth().get_token_expiry()
		except InvalidTokenError:
			raise InvalidTokenError("Unable to read token expiry time")

		if self.check_expired(expiry):
			try:
				result = self._session.get(req.get_url(), headers=req.get_header(), timeout=(5, 30))
			except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
				logger.error(f"Error with request {e}")

		if result.ok:
			try:
				result_text = result.text
				return result_text
			except ValueError as e:
				logger.error(f"Error reading request body {e}")
		else:
			raise RequestFailedError(f"Error with request HTTP error {result.status_code}")

	def post(self, req: AnaplanRequest):
		expiry: float
		result: requests.Response

		try:
			expiry = self._conn.get_auth().get_token_expiry()
		except InvalidTokenError:
			raise InvalidTokenError("Unable to read token expiry time")

		if self.check_expired(expiry):
			try:
				result = self._session.get(req.get_url(), headers=req.get_header(), json=req.get_body(), timeout=(5, 30))
			except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
				logger.error(f"Error with request {e}")

		if result.ok:
			try:
				result_text = result.text
				return result_text
			except ValueError as e:
				logger.error(f"Error reading request body {e}")
		else:
			raise RequestFailedError(f"Error with request HTTP error {result.status_code}")

	def put(self, req: AnaplanRequest):
		expiry: float
		result: requests.Response

		try:
			expiry = self._conn.get_auth().get_token_expiry()
		except InvalidTokenError:
			raise InvalidTokenError("Unable to read token expiry time")

		if self.check_expired(expiry):
			try:
				result = self._session.put(req.get_url(), headers=req.get_header(), data=req.get_body(), timeout=(5, 30))
			except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
				logger.error(f"Error with request {e}")

		if result.ok:
			try:
				result_text = result.text
				return result_text
			except ValueError as e:
				logger.error(f"Error reading request body {e}")
		else:
			raise RequestFailedError(f"Error with request HTTP error {result.status_code}")
