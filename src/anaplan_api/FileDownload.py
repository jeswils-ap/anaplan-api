import logging
import requests
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from .File import File
from .AnaplanConnection import AnaplanConnection
from .AnaplanResourceFile import AnaplanResourceFile
from .util.AnaplanVersion import AnaplanVersion

logger = logging.getLogger(__name__)


class FileDownload(File):
	_base_url = f"https://api.anaplan.com/{AnaplanVersion.major()}/{AnaplanVersion.minor()}/workspaces/"
	_conn: AnaplanConnection
	_file_resources: AnaplanResourceFile
	_file_id: str
	_workspace: str
	_model: str
	_url: str
	_chunk_count: int

	def set_chunk_count(self):
		"""Sets the chunk count of the specified file to download based on Anaplan metadata"""
		_chunk_count = super().get_chunk_count()

	def download_file(self) -> str:
		"""Download all chunks of the specified file from Anaplan

		:raises HTTPError: HTTP error code
		:raises ConnectionError: Network-related errors
		:raises SSLError: Server-side SSL certificate errors
		:raises Timeout: Request timeout errors
		:raises ConnectTimeout: Timeout error when attempting to connect
		:raises ReadTimeout: Timeout error waiting for server response
		:return: Contents of the specified file.
		:rtype: str
		"""
		conn = self._conn
		url = ''.join([super().get_url(), "/chunks/"])
		current_chunk = 0

		file_data = []
		file_contents = {}

		get_header = {
			"Authorization": conn.get_auth().get_auth_token(),
		}

		while int(current_chunk) < int(self._chunk_count):
			try:
				logger.debug(f"Downloading chunk {current_chunk}")
				file_contents = requests.get(''.join([url, str(current_chunk)]), headers=get_header, timeout=(5, 30)).text
			except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
				logger.error(f"Error downloading chunk {e}", exc_info=True)
				raise Exception(f"Error downloading chunk {e}")
			if file_contents:
				logger.debug(f"Chunk {current_chunk} downloaded successfully.")
				file_data.append(file_contents)
			else:
				logger.error(f"There was a problem downloading {self._file_id}")
				break
			current_chunk = str(int(current_chunk) + 1)

		if int(current_chunk) == int(self._chunk_count):
			logger.info("File download complete!")
			return ''.join(file_data)
