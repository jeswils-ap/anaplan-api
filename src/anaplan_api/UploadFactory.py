import os
from typing import Union
from .AnaplanConnection import AnaplanConnection
from .FileUpload import FileUpload
from .StreamUpload import StreamUpload


class UploadFactory:
	_is_file: bool

	def __init__(self, data: str):
		self._is_file = os.path.isfile(data)

	def get_uploader(self, conn: AnaplanConnection, file_id: str) -> Union[FileUpload, StreamUpload]:
		if self._is_file:
			return FileUpload(conn, file_id)
		else:
			return StreamUpload(conn, file_id)
