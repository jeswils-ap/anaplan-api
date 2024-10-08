import logging
from functools import partial
from io import StringIO, BytesIO
from .Upload import Upload

logger = logging.getLogger(__name__)


class StreamUpload(Upload):
    def upload(self, chunk_size, data):
        """Upload data held in memory to Anaplan model

        :param chunk_size: Upload request body size in MB between 1 and 50
        :type chunk_size: int
        :param data: String data to be uploaded to Anaplan
        :type data: str
        """

        stream_upload = False
        endpoint = f"{super().endpoint}"
        io_data = StringIO(data)  # Convert str to StingIO for enumeration

        try:
            io_bytes = BytesIO(data.encode('utf-8'))
        except TypeError as e:
            logger.error(f"Error converting data to bytes: {e}", exc_info=True)
            raise TypeError(f"Error converting data to bytes: {e}")
        except MemoryError as e:
            logger.error(f"Error converting data to BytesIO: {e}", exc_info=True)
            raise MemoryError(f"Error converting data to BytesIO: {e}")

        metadata_update = super().file_metadata(
            endpoint
        )  # Update file metadata to begin upload process

        if metadata_update:
            logger.info(f"Starting upload of file {super().file_id}.")
            # Loop through enumerated data, sending chunks of the specified size to Anaplan until all data is uploaded
            for chunk_num, chunk in enumerate(
                iter(partial(io_bytes.read, chunk_size * (1024**2)), b"")
            ):
                if not chunk:
                    break
                stream_upload = super().file_data(
                    f"{endpoint}chunks/{str(chunk_num)}",
                    chunk_num,
                    chunk
                )

            # Once all data is uploaded mark the file complete to indicate the file is ready for use
            if stream_upload:
                complete_upload = super().file_metadata(f"{endpoint}complete")
                if complete_upload:
                    logger.info(f"Upload of file {super().file_id} complete.")
