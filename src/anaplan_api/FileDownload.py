import logging
import requests
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from .File import File
from .AnaplanConnection import AnaplanConnection
from .AnaplanResourceFile import AnaplanResourceFile

logger = logging.getLogger(__name__)


class FileDownload(File):
	_base_url: str = "https://api.anaplan.com/2/0/workspaces/"
	_conn: AnaplanConnection
	_file_resources: AnaplanResourceFile
	_file_id: str
	_workspace: str
	_model: str
	_url: str
	_chunk_count: int

	def set_chunk_count(self):
		_chunk_count = super().get_chunk_count()

	def download_file(self):
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
