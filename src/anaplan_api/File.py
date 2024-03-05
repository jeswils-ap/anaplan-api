from __future__ import annotations
from typing import TYPE_CHECKING
from .Resources import Resources
from .ResourceParserFile import ResourceParserFile
from .util.Util import ResourceNotFoundError

if TYPE_CHECKING:
    from .AnaplanConnection import AnaplanConnection
    from .AnaplanResourceFile import AnaplanResourceFile
    from .util.RequestHandler import RequestHandler


class File:
    """A class representing an Anaplan file.

    :param _handler: Class for issuing API requests
    :type _handler: RequestHandler
    :param _conn: Object with authentication, workspace, and model details.
    :type _conn: AnaplanConnection
    :param _file_resources: Object with file metadata
    :type _file_resources: AnaplanResourceFile
    :param _file_id: ID of file in Anaplan
    :type _file_id: str
    :param _workspace: ID of workspace that contains the specified Anaplan model
    :type _workspace: str
    :param _model: ID of the Anaplan model hosting specified file.
    :type _model: str
    :param _url: Appended _base_url to interact with the specified file.
    :type _url: str
    :param _chunk_count: Number of chunk segments of the specified file.
    :type _chunk_count: int
    """

    _handler: RequestHandler
    _conn: AnaplanConnection
    _file_resources: AnaplanResourceFile
    _endpoint: str
    _file_id: str
    _workspace: str
    _model: str
    _url: str
    _chunk_count: int

    def __init__(
        self, handler: RequestHandler, conn: AnaplanConnection, file_id: str, **kwargs
    ):
        """
        :param conn: Object with authentication, workspace, and model details
        :type conn: AnaplanConnection
        :param file_id: ID of the specified file in the Anaplan model
        :type file_id: str
        """
        self._handler = handler
        self._conn = conn
        self._file_id = file_id
        self._workspace = conn.workspace
        self._model = conn.model
        self._endpoint = f"workspaces/{self._workspace}/models/{self._model}/files/{self._file_id}/"

        self.get_metadata()
        self.set_file_details()

    def get_metadata(self):
        """
        Instantiates Resources class to fetch files list from Anaplan, then parses to build an AnaplanResource object
        """
        conn = self._conn  # Reading class variable to pass to external class
        get_files = Resources(conn, "files")
        file_list = get_files.get_resources()
        file_parser = ResourceParserFile()
        self._file_resources = file_parser.get_parser(file_list)

    def set_file_details(self):
        """Sets _chunk_count corresponding to the matching Anaplan file in the AnaplanResource object.

        :raises ResourceNotFoundError: If specified file ID is not found in AnaplanResource object
        """
        try:
            self._chunk_count = self._file_resources[self._file_id]
        except ResourceNotFoundError:
            raise ResourceNotFoundError(f"{self._file_id} not found.")

    @property
    def handler(self) -> RequestHandler:
        return self._handler

    @property
    def connection(self) -> AnaplanConnection:
        """Returns the AnaplanConnection object.

        :return: Object with connection details for a specified model
        :rtype: AnaplanConnection
        """
        return self._conn

    @property
    def file_id(self) -> str:
        """Returns the ID of the specified Anaplan file.

        :return: Anaplan file file_id
        :rtype: str
        """
        return self._file_id

    @file_id.setter
    def file_id(self, file_id: str):
        """Updates the specified file ID and updates _chunk_count to match.

        :param file_id: ID of file in Anaplan.
        :type file_id: str
        :raises ResourceNotFoundError: If specified file ID is not found in AnaplanResource object
        """
        self._file_id = file_id
        try:
            self._chunk_count = self._file_resources[self._file_id]
        except ResourceNotFoundError:
            raise ResourceNotFoundError(f"{self._file_id} not found.")

    @property
    def workspace(self) -> str:
        """Returns the AnaplanResource object.

        :return: Workspace ID
        :rtype: str
        """
        return self._workspace

    @property
    def model(self) -> str:
        """Returns the AnaplanResource object.

        :return: Anaplan model ID
        :rtype: str
        """
        return self._model

    @property
    def resource(self) -> AnaplanResourceFile:
        """Returns the AnaplanResource object.

        :return: AnaplanResource object with files in specified Anaplan model
        :rtype: AnaplanResourceFile
        """
        return self._file_resources

    @property
    def chunk_count(self) -> int:
        """Returns _chunk_count of the specified file.

        :return: Chunk count of specified file.
        :rtype: int
        """
        return self._chunk_count

    @property
    def endpoint(self) -> str:
        """Returns the URL of the specified Anaplan file.

        :return: API URL of specified file
        :rtype: str
        """
        return self._endpoint
