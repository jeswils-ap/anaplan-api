from __future__ import annotations
from typing import TYPE_CHECKING, List
from dataclasses import dataclass

if TYPE_CHECKING:
    from pandas import DataFrame
    from .ParserResponse import ParserResponse


@dataclass
class ActionResponse:
    _responses: List[ParserResponse]
    _error_dumps: List[DataFrame]
    _files: List[str]

    @property
    def reponses(self) -> List[ParserResponse]:
        return self._responses

    @property
    def dumps_available(self) -> bool:
        return False if self._error_dumps is None else True

    @property
    def error_dumps(self) -> List[DataFrame]:
        return self._error_dumps

    @property
    def files_available(self) -> bool:
        return False if self._files is None else True

    @property
    def files(self) -> List[str]:
        return self._files
