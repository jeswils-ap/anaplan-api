import logging
from functools import partial
from io import StringIO
from .Upload import Upload

logger = logging.getLogger(__name__)


class StreamUpload(Upload):
	def upload(self, chunk_size, data):
		"""
		:param chunk_size: Upload request body size in MB between 1 and 50
		:param data: String data to be uploaded to Anaplan
		"""

		stream_upload = False
		url = ''.join([super().get_base_url(), super().get_workspace(), "/models/", super().get_model(), "/files/",
		               super().get_file_id()])
		io_data = StringIO(data)
		metadata_update = super().file_metadata(url)

		if metadata_update:
			logger.info(f"Starting upload of file {super().get_file_id()}.")
			for chunk_num, data in enumerate(iter(partial(io_data.read, chunk_size * (1024 ** 2)), '')):
				stream_upload = super().file_data(''.join([url, "/chunks/", str(chunk_num)]), chunk_num,
				                                  data.encode('utf-8'))

			if stream_upload:
				complete_upload = super().file_metadata(''.join([url, "/complete"]))
				if complete_upload:
					logger.info(f"Upload of file {super().get_file_id()} complete.")
