import os
from typing import Union
from .AnaplanConnection import AnaplanConnection
from .FileUpload import FileUpload
from .StreamUpload import StreamUpload
from .util.RequestHandler import RequestHandler


class UploadFactory:
    _is_file: bool

    def __init__(self, data: str):
        """
        :param data: Filepath or data to upload
        """
        self._is_file = os.path.isfile(data)

    def get_uploader(
        self, handler: RequestHandler, conn: AnaplanConnection, file_id: str
    ) -> Union[FileUpload, StreamUpload]:
        """If initialized data source is a filepath, return initialized object for file upload otherwise return
           object for stream upload.

        :param handler: Class for handling API requests
        :type handler: RequestHandler
        :param conn: AnaplanConnection object containing Workspace and Model ID, and AuthToken object
        :type conn: AnaplanConnection
        :param file_id: ID of the file to upload
        :type file_id: str
        :return: Initialized upload object
        :rtype: Union[FileUpload, StreamUpload]
        """
        if self._is_file:
            return FileUpload(handler, conn, file_id)
        else:
            return StreamUpload(handler, conn, file_id)
