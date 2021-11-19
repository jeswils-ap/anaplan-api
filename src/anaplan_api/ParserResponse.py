from dataclasses import dataclass
from pandas import DataFrame
from typing import Optional


@dataclass
class ParserResponse:
    _task_detail: str
    _export_file: Optional[str]
    _error_dump: bool
    _error_dump_file: Optional[DataFrame]

    def __init__(self, task_detail: str, export_file: str, error_dump: bool, error_dump_file: DataFrame):
        self._task_detail = task_detail
        self._export_file = export_file
        self._error_dump = error_dump
        self._error_dump_file = error_dump_file

    def __str__(self):
        return self._task_detail

    def __bool__(self):
        return self._error_dump

    def get_task_detail(self) -> str:
        return self._task_detail

    def get_export_file(self) -> Optional[str]:
        return self._export_file

    def get_error_dump(self) -> Optional[DataFrame]:
        return self._error_dump_file
