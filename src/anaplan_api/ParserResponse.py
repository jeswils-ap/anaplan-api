from dataclasses import dataclass
from pandas import DataFrame
from typing import Optional


@dataclass
class ParserResponse:
    """Represents a set of friendly task response data

    :param _task_detail: Overall task information
    :type _task_detail: str
    :param _export_file: File exported from Anaplan model
    :type _export_file: Optional[str]
    :param _error_dump: Whether error dump was generated for a task
    :type _error_dump: bool
    :param _error_dump_file: Error dump data
    :type _error_dump_file: Optional[DataFrame]
    """
    _task_detail: str
    _export_file: Optional[str]
    _error_dump: bool
    _error_dump_file: Optional[DataFrame]

    def __init__(self, task_detail: str, export_file: str, error_dump: bool, error_dump_file: DataFrame):
        self._task_detail = task_detail
        self._export_file = export_file
        self._error_dump = error_dump
        self._error_dump_file = error_dump_file

    def __str__(self) -> str:
        """Get overall task results

        :return: Task details
        :rtype: str
        """
        return self._task_detail

    def __bool__(self) -> bool:
        """Check whether error dump was generated

        :return: Whether error dump exists
        :rtype: bool
        """
        return self._error_dump

    def get_task_detail(self) -> str:
        """Get overall task results

        :return: Task details
        :rtype: str
        """
        return self._task_detail

    def file_exists(self) -> bool:
        """Check whether Anaplan export file has data

        :return: Whether export file exists
        :rtype: bool
        """
        return True if self._export_file is not None else False

    def get_export_file(self) -> Optional[str]:
        """Get downloaded file

        :return: Exported Anaplan file
        :rtype: Optional[str]
        """
        return self._export_file

    def get_error_dump(self) -> Optional[DataFrame]:
        """Get error dump

        :return: Error dump
        :rtype: Optional[DataFrame]
        """
        return self._error_dump_file
