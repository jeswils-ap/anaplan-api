from dataclasses import dataclass


@dataclass(frozen=True)
class ParserResponse:
    """Represents a set of friendly task response data

    :param _raw_response: Raw response from Anaplan server
    :type _raw_response: dict
    :param _task_detail: Overall task information
    :type _task_detail: str
    :param _error_dump: Whether error dump was generated for a task
    :type _error_dump: bool
    :param _file_download: Whether an export file is available for download
    :type _file_download: bool
    """

    _raw_response: dict
    _task_detail: str
    _task_endpoint: str
    _file_id: str
    _error_dump: bool
    _file_download: bool

    @property
    def raw_response(self) -> dict:
        return self._raw_response

    @property
    def task_detail(self) -> str:
        """Get overall task results

        :return: Task details
        :rtype: str
        """
        return self._task_detail

    @property
    def task_endpoint(self) -> str:
        return self._task_endpoint

    @property
    def file_id(self) -> str:
        return self._file_id

    @property
    def dump(self) -> bool:
        """Check whether Anaplan export file has data

        :return: Whether export file exists
        :rtype: bool
        """
        return self._error_dump

    @property
    def file(self) -> bool:
        """Get downloaded file

        :return: Exported Anaplan file
        :rtype: Optional[str]
        """
        return self._file_download
