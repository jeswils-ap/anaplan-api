import logging
from functools import partial
from .Upload import Upload

logger = logging.getLogger(__name__)


class FileUpload(Upload):
    def upload(self, chunk_size: int, file: str):
        """Upload a local file to Anaplan model

        :param chunk_size: Desired size of the chunk, in megabytes
        :type chunk_size: int
        :param file: Path to the local file to be uploaded to Anaplan
        :type file: str
        """
        endpoint = f"{super().endpoint}"

        metadata_update = super().file_metadata(endpoint)
        # Confirm that the metadata update for the requested file was OK before proceeding with file upload
        if metadata_update:
            logger.info(f"Starting upload of file {super().file_id}.")

            try:
                with open(file, "rt") as file:
                    # Enumerate the file contents in specified chunk size
                    for chunk_num, data in enumerate(
                        iter(partial(file.read, chunk_size * (1024**2)), "")
                    ):
                        if not data:
                            break
                        complete = super().file_data(
                            f"{endpoint}chunks/{str(chunk_num)}",
                            chunk_num,
                            data.encode("utf-8"),
                        )
            except OSError as e:
                logger.error(f"Error opening file {file}: {e}", exc_info=True)
                raise OSError(f"Error opening file {file}: {e}")

            if complete:
                complete_upload = super().file_metadata(f"{endpoint}complete")
                if complete_upload:
                    logger.info(f"Upload of file {super().file_id} complete.")
