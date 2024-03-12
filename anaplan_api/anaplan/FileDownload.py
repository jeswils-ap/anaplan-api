from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from .File import File
from .models.AnaplanVersion import AnaplanVersion

if TYPE_CHECKING:
    from .models.AnaplanConnection import AnaplanConnection
    from .models.AnaplanResourceFile import AnaplanResourceFile
    from .util.RequestHandler import RequestHandler

logger = logging.getLogger(__name__)


class FileDownload(File):
    _handler: RequestHandler
    _base_url = f"https://api.anaplan.com/{AnaplanVersion().major}/{AnaplanVersion().minor}/workspaces/"
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
        endpoint = "".join([super().get_endpoint(), "/chunks/"])
        current_chunk = 0

        file_data = []
        file_contents = {}

        get_header = {
            "Authorization": conn.authorization.token_value,
        }

        while int(current_chunk) < int(self._chunk_count):
            try:
                logger.debug(f"Downloading chunk {current_chunk}")
                file_contents = self._handler.make_request(
                    "".join([endpoint, str(current_chunk)]), "GET", headers=get_header
                ).text
            except Exception as e:
                logger.error(f"Error downloading chunk {e}", exc_info=True)
                raise Exception(f"Error downloading chunk {e}")
            if not file_contents:
                logger.error(f"There was a problem downloading {self._file_id}")
                break

            logger.debug(f"Chunk {current_chunk} downloaded successfully.")
            file_data.append(file_contents)
            current_chunk = str(int(current_chunk) + 1)

        logger.info("File download complete!")
        return "".join(file_data)
