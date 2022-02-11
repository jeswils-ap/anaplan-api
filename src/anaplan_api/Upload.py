# ===============================================================================
# Created:			1 Nov 2021
# @author:			Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:		Abstract Anaplan Authentication Class
# Input:			Username & Password, or SHA keypair
# Output:			Anaplan JWT and token expiry time
# ===============================================================================
import logging
import requests
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from .File import File

logger = logging.getLogger(__name__)


class Upload(File):

	def get_base_url(self) -> str:
		"""Get base URL for Anaplan API

		:return: Anaplan API base URL
		:rtype: str
		"""
		return super().get_base_url()

	def get_workspace(self) -> str:
		"""Get the workspace ID

		:return: Workspace ID for the specified model
		:rtype: str
		"""
		return super().get_workspace()

	def get_model(self) -> str:
		"""Get the model ID

		:return: ID of the specified model
		:rtype: str
		"""
		return super().get_model()

	def get_file_id(self) -> str:
		"""Get the ID of the specified file

		:return: ID of the specified file
		:rtype: str
		"""
		return super().get_file_id()

	def upload(self, chunk_size: int, file: str):
		pass

	def file_metadata(self, url: str) -> bool:
		"""Update file metadata in Anaplan model as first step in file upload process

		:param url: URL of the specified file
		:raises HTTPError: HTTP error code
		:raises ConnectionError: Network-related errors
		:raises SSLError: Server-side SSL certificate errors
		:raises Timeout: Request timeout errors
		:raises ConnectTimeout: Timeout error when attempting to connect
		:raises ReadTimeout: Timeout error waiting for server response
		:return: Whether metadata was successfully updated
		:rtype: bool
		"""
		authorization = super().get_connection().get_auth().get_auth_token()

		file_id = super().get_file_id()

		post_header = {
						"Authorization": authorization,
						"Content-Type": "application/json"
			}

		stream_metadata = {
							"id": file_id,
							"chunkCount": -1
			}

		meta_post = None
		try:
			logger.debug("Updating file metadata.")
			meta_post = requests.post(url, headers=post_header, json=stream_metadata, timeout=(5, 30))
			logger.debug("Complete!")
		except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
			logger.error(f"Error setting metadata {e}", exc_info=True)
			raise Exception(f"Error setting metadata {e}")

		if meta_post.ok:
			return True
		else:
			return False

	def file_data(self, url: str, chunk_num: int, data: str) -> bool:
		"""Upload data chunk to the specified file

		:param url: URL of the  specified file
		:type url: str
		:param chunk_num: ID of the chunk being uploaded
		:type chunk_num: int
		:param data: Data to upload
		:type data: str
		:raises HTTPError: HTTP error code
		:raises ConnectionError: Network-related errors
		:raises SSLError: Server-side SSL certificate errors
		:raises Timeout: Request timeout errors
		:raises ConnectTimeout: Timeout error when attempting to connect
		:raises ReadTimeout: Timeout error waiting for server response
		:return: Whether file data upload was successful
		:rtype: bool
		"""

		authorization = super().get_connection().get_auth().get_auth_token()

		put_header = {
						"Authorization": authorization,
						"Content-Type": "application/octet-stream"
			}

		stream_upload = None
		try:
			logger.debug(f"Attempting to upload chunk {chunk_num + 1}")
			stream_upload = requests.put(url, headers=put_header, data=data, timeout=(5, 30))
			logger.debug(f"Chunk {chunk_num + 1} uploaded successfully.")
		except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
			logger.error(f"Error uploading chunk {chunk_num + 1}, {e}", exc_info=True)
			raise Exception(f"Error uploading chunk {chunk_num + 1}, {e}")

		if stream_upload.ok:
			return True
		else:
			return False
