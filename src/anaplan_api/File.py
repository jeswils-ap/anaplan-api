from .AnaplanConnection import AnaplanConnection
from .Resources import Resources
from .ResourceParserFile import ResourceParserFile
from .AnaplanResourceFile import AnaplanResourceFile
from .util.AnaplanVersion import AnaplanVersion
from .util.Util import ResourceNotFoundError


class File:
    """
    A class representing an Anaplan file.

    Attributes:
    _conn : AnaplanConnection
        Object with authentication, workspace, and model details.
    _file_resources : AnaplanResourceFile
        Object with file metadata
    _base_url : str
        Anaplan API URL
    _file_id : str
        ID of file in Anaplan
    _workspace : str
        ID of workspace that contains the specified Anaplan model
    _model : str
        ID of the Anaplan model hosting specified file.
    _url : str
        Appended _base_url to interact with the specified file.
    _chunk_count : int
        Number of chunk segments of the specified file.

    Methods:
    get_metadata()
        Instantiates Resources class to fetch files list from Anaplan, then parses to build an AnaplanResource object.
    get_file_details()
        sets _chunk_count corresponding to the matching Anaplan file in the AnaplanResource object.
    get_resource()
        Returns the AnaplanResource object.
    get_chunk_count():
        Returns _chunk_count of the specified file.
    get_url()
        Returns the URL of the specified Anaplan file.
    set_file_id()
        Updates the specified file ID and updates _chunk_count to match.
    """

    _conn: AnaplanConnection
    _file_resources: AnaplanResourceFile
    _base_url = f"https://api.anaplan.com/{AnaplanVersion.major()}/{AnaplanVersion.minor()}/workspaces/"
    _file_id: str
    _workspace: str
    _model: str
    _url: str
    _chunk_count: int

    def __init__(self, conn: AnaplanConnection, file_id: str):
        """
        :param conn:
        :param file_id:
        """
        self._conn = conn
        self._file_id = file_id
        self._workspace = conn.get_workspace()
        self._model = conn.get_model()
        self._url = ''.join([self._base_url, self._workspace, "/models/", self._model, "/files/", file_id])

        self.get_metadata()
        self.get_file_details()

    def get_metadata(self):
        """
        :return: None
        """
        conn = self._conn  # Reading class variable to pass to external class
        get_files = Resources(conn, "files")
        file_list = get_files.get_resources()
        file_parser = ResourceParserFile()
        self._file_resources = file_parser.get_parser(file_list)

    def get_file_details(self):
        """
        Raises:
        ResourceNotFoundError
            If specified file ID is not found in AnaplanResource object
        """
        try:
            self._chunk_count = self._file_resources[self._file_id]
        except ResourceNotFoundError:
            raise ResourceNotFoundError(f"{self._file_id} not found.")

    def get_base_url(self) -> str:
        return self._base_url

    def get_connection(self) -> AnaplanConnection:
        return self._conn

    def get_file_id(self) -> str:
        return self._file_id

    def get_workspace(self) -> str:
        return self._workspace

    def get_model(self) -> str:
        return self._model

    def get_resource(self):
        """
        :return: AnaplanResource object with files in specified Anaplan model
        """
        return self._file_resources

    def get_chunk_count(self):
        """
        :return: Chunk count of specified file.
        """
        return self._chunk_count

    def get_url(self):
        """
        :return: API URL of specified file
        """
        return self._url

    def set_file_id(self, file_id: str):
        """
        :param file_id: ID of file in Anaplan.
        Raises:
        ResourceNotFoundError
            If specified file ID is not found in AnaplanResource object
        """
        self._file_id = file_id
        try:
            self._chunk_count = self._file_resources[self._file_id]
        except ResourceNotFoundError:
            raise ResourceNotFoundError(f"{self._file_id} not found.")
