import logging
from functools import partial
from .Upload import Upload

logger = logging.getLogger(__name__)


class FileUpload(Upload):
	def upload(self, chunk_size: int, file: str):
		"""
		:param chunk_size: Desired size of the chunk, in megabytes
		:param file: Path to the local file to be uploaded to Anaplan
		:return: None
		"""

		url = ''.join([super().get_base_url(), super().get_workspace(), "/models/", super().get_model(), "/files/",
		               super().get_file_id()])

		metadata_update = super().file_metadata(url)
		# Confirm that the metadata update for the requested file was OK before proceeding with file upload
		if metadata_update:
			logger.info("Starting file upload.")

			with open(file, 'rt') as file:
				chunk_num = 0

				for data in iter(partial(file.read, chunk_size * (1024 ** 2)), ''):
					complete = super().file_data(''.join([url, "/chunks/", str(chunk_num)]), chunk_num,
					                             data.encode('utf-8'))
					chunk_num += 1

			if complete:
				complete_upload = super().file_metadata(''.join([url, "/complete"]))
				if complete_upload:
					logger.info("File upload complete, ")
