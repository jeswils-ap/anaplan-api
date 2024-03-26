# ===============================================================================
# Created:			1 Nov 2021
# @author:			Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:		Abstract Anaplan Authentication Class
# Input:			Username & Password, or SHA keypair
# Output:			Anaplan JWT and token expiry time
# ===============================================================================
import logging
import io
import json
import gzip
from .File import File

logger = logging.getLogger(__name__)


class Upload(File):

    @property
    def endpoint(self) -> str:
        """Get base URL for Anaplan API

        :return: Anaplan API base URL
        :rtype: str
        """
        return super().endpoint

    @property
    def workspace(self) -> str:
        """Get the workspace ID

        :return: Workspace ID for the specified model
        :rtype: str
        """
        return super().workspace

    @property
    def model(self) -> str:
        """Get the model ID

        :return: ID of the specified model
        :rtype: str
        """
        return super().model

    @property
    def file_id(self) -> str:
        """Get the ID of the specified file

        :return: ID of the specified file
        :rtype: str
        """
        return super().file_id

    def upload(self, chunk_size: int, file: str):
        pass

    def file_metadata(self, endpoint: str) -> bool:
        """Update file metadata in Anaplan model as first step in file upload process

        :param endpoint: URL of the specified file
        :raises Exception: Exception from RequestHandler exception group
        :return: Whether metadata was successfully updated
        :rtype: bool
        """
        authorization = super().connection.authorization.token_value

        file_id = super().file_id

        post_header = {
            "Authorization": authorization,
            "Content-Type": "application/json",
        }

        stream_metadata = {"id": file_id, "chunkCount": -1}

        try:
            logger.debug("Updating file metadata.")
            meta_post = super().handler.make_request(
                endpoint, "POST", headers=post_header, data=json.dumps(stream_metadata)
            )
            logger.debug("Complete!")
        except Exception as e:
            logger.error(f"Error setting metadata {e}", exc_info=True)
            raise Exception(f"Error setting metadata {e}")

        return True

    def file_data(self, url: str, chunk_num: int, data: str) -> bool:
        """Upload data chunk to the specified file

        :param url: URL of the  specified file
        :type url: str
        :param chunk_num: ID of the chunk being uploaded
        :type chunk_num: int
        :param data: Data to upload
        :type data: str
        :raises Exception: Exception from RequestHandler exception group
        :return: Whether file data upload was successful
        :rtype: bool
        """

        authorization = super().connection.authorization.token_value

        put_header = {
            "Authorization": authorization,
            "Content-Type": "application/octet-stream",
        }

        try:
            logger.debug(f"Attempting to upload chunk {chunk_num + 1}")
            stream_upload = super().handler.make_request(
                url, "PUT", headers=put_header, data=data
            )
            logger.debug(f"Chunk {chunk_num + 1} uploaded successfully.")
        except Exception as e:
            logger.error(f"Error uploading chunk {chunk_num + 1}, {e}", exc_info=True)
            raise Exception(f"Error uploading chunk {chunk_num + 1}, {e}")

        return True

    @staticmethod
    def compress_data(upload_data: bytes):
        output = io.BytesIO()
        with gzip.GzipFile(fileobj=output, mode="wb") as gz_stream:
            gz_stream.write(upload_data)
        compressed_data = output.getvalue()
        return compressed_data
