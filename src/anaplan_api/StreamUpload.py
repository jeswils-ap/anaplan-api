import os, logging
from io import StringIO
from anaplan_api.Upload import Upload

logger = logging.getLogger(__name__)

class StreamUpload(Upload):
	def upload(self, chunk_size, data):
		'''
		:param conn: AnaplanConnection object which contains authorization string, workspace ID, and model ID
		:param fileId: ID of the file in the Anaplan model
		:param buffer: data to uplaod to Anaplan file
		:param *args: Once complete, this should be True to complete upload and reset chunk counter
		'''

		url = ''.join([super().get_base_url(), "/", super().get_workspace(), "/models/", super().get_model(), "/files/", super().get_file_id()])


		ioData = StringIO(data)
		#Find length of data stream
		ioDataEnd = ioData.seek(0, os.SEEK_END)
		#Reset index back to 0 for reading
		ioData.seek(0)

		metadata_update = super().file_metadata(url)

		if metadata_update:
			logger.info("Starting file upload...")
			chunk_num = 0
			while ioData.tell() != ioDataEnd:
				data = ioData.read(chunk_size * (1024 * 1024))
				stream_upload = super().file_data(''.join([url, "/chunks/", str(chunk_num)]), chunk_num, data.encode('utf-8'))
				chunk_num += 1

			if stream_upload:
				complete_upload = super().file_metadata(''.join([url,"/complete"]))
				if complete_upload:
					logger.info("File upload complete.")
