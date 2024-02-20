from .AnaplanConnection import AnaplanConnection
from .Resources import Resources
from .ResourceParserFile import ResourceParserFile
from .AnaplanResourceFile import AnaplanResourceFile
from .util.AnaplanVersion import AnaplanVersion
from .util.Util import ResourceNotFoundError


class File:
    """A class representing an Anaplan file.

    :param _conn: Object with authentication, workspace, and model details.
    :type _conn: AnaplanConnection
    :param _file_resources: Object with file metadata
    :type _file_resources: AnaplanResourceFile
    :param _base_url: Anaplan API URL
    :type _base_url: str
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

    _conn: AnaplanConnection
    _file_resources: AnaplanResourceFile
    _base_url: str = f"https://api.anaplan.com/{AnaplanVersion.major}/{AnaplanVersion.minor}/workspaces/"
    _file_id: str
    _workspace: str
    _model: str
    _url: str
    _chunk_count: int

    def __init__(self, conn: AnaplanConnection, file_id: str):
        """
        :param conn: Object with authentication, workspace, and model details
        :type conn: AnaplanConnection
        :param file_id: ID of the specified file in the Anaplan model
        :type file_id: str
        """
        self._conn = conn
        self._file_id = file_id
        self._workspace = conn.get_workspace()
        self._model = conn.get_model()
        self._url = ''.join([self._base_url, self._workspace, "/models/", self._model, "/files/", file_id])

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

    def get_base_url(self) -> str:
        """Return the base URL for Anaplan API.

        :return: Base URL for Anaplan API.
        :rtype: str
        """
        return self._base_url

    def get_connection(self) -> AnaplanConnection:
        """Returns the AnaplanConnection object.

        :return: Object with connection details for a specified model
        :rtype: AnaplanConnection
        """
        return self._conn

    def get_file_id(self) -> str:
        """Returns the ID of the specified Anaplan file.

        :return: Anaplan file file_id
        :rtype: str
        """
        return self._file_id

    def get_workspace(self) -> str:
        """Returns the AnaplanResource object.

        :return: Workspace ID
        :rtype: str
        """
        return self._workspace

    def get_model(self) -> str:
        """Returns the AnaplanResource object.

        :return: Anaplan model ID
        :rtype: str
        """
        return self._model

    def get_resource(self) -> AnaplanResourceFile:
        """Returns the AnaplanResource object.

        :return: AnaplanResource object with files in specified Anaplan model
        :rtype: AnaplanResourceFile
        """
        return self._file_resources

    def get_chunk_count(self) -> int:
        """Returns _chunk_count of the specified file.

        :return: Chunk count of specified file.
        :rtype: int
        """
        return self._chunk_count

    def get_url(self) -> str:
        """Returns the URL of the specified Anaplan file.

        :return: API URL of specified file
        :rtype: str
        """
        return self._url

    def set_file_id(self, file_id: str):
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
