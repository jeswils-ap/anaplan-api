from __future__ import annotations
from typing import Union, TYPE_CHECKING
import os
from .FileUpload import FileUpload
from .StreamUpload import StreamUpload

if TYPE_CHECKING:
    from .AnaplanConnection import AnaplanConnection


class UploadFactory:
    _is_file: bool

    def __init__(self, data: str):
        """
        :param data: Filepath or data to upload
        """
        self._is_file = os.path.isfile(data)

    def get_uploader(
        self, conn: AnaplanConnection, file_id: str
    ) -> Union[FileUpload, StreamUpload]:
        """If initialized data source is a filepath, return initialized object for file upload otherwise return
           object for stream upload.

        :param conn: AnaplanConnection object containing Workspace and Model ID, and AuthToken object
        :type conn: AnaplanConnection
        :param file_id: ID of the file to upload
        :type file_id: str
        :return: Initialized upload object
        :rtype: Union[FileUpload, StreamUpload]
        """
        if self._is_file:
            return FileUpload(conn, file_id)
        else:
            return StreamUpload(conn, file_id)
