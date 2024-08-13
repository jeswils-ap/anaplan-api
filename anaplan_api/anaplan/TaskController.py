from __future__ import annotations
from typing import TYPE_CHECKING, List
import logging
from io import StringIO
import pandas as pd
from pandas.errors import EmptyDataError, ParserError, ParserWarning

from .TaskFactoryGenerator import TaskFactoryGenerator
from .FileDownload import FileDownload
from .models.ActionResponse import ActionResponse
from .util.RequestHandler import RequestHandler
from .models.AnaplanVersion import AnaplanVersion

if TYPE_CHECKING:
    from .Action import Action
    from .Parser import Parser
    from .models.AnaplanConnection import AnaplanConnection
    from .models.ParserResponse import ParserResponse
    from pandas import DataFrame

logger = logging.getLogger(__name__)


class TaskController:
    _conn: AnaplanConnection
    _action_id: str
    _retry_count: int
    _mapping_params: dict
    _handler: RequestHandler = RequestHandler(AnaplanVersion().base_url)
    _task_id: str
    _parser_responses: List[ParserResponse]
    _response: ActionResponse
    _action: Action
    _parser: Parser

    def __init__(
        self,
        conn: AnaplanConnection,
        action_id: str,
        retry_count: int,
        mapping_params: dict = None,
    ):
        self._conn = conn
        self._action_id = action_id
        self._retry_count = retry_count
        self._mapping_params = mapping_params
        self._response = self._execute()

    @property
    def response(self) -> ActionResponse:
        return self._response

    def _execute(self) -> ActionResponse:
        generator = TaskFactoryGenerator(self._action_id[:3])
        factory = generator.get_factory()

        self._action = factory.get_action(
            conn=self._conn,
            action_id=self._action_id,
            retry_count=self._retry_count,
            mapping_params=self._mapping_params,
        )
        task = self._action.execute()
        self._task_id = task.results["taskId"]

        parser = factory.get_parser(conn=self._conn, results=task.results, url=task.url)
        self._parser_responses = parser.results

        dumps: List[DataFrame] = list()
        files: List[str] = list()
        for response in self._parser_responses:
            if response.dump:
                dumps.append(self.get_error_dump(response.task_endpoint))
                pass
            if response.file:
                files.append(
                    FileDownload(
                        conn=self._conn, file_id=response.file_id
                    ).download_file()
                )

        return ActionResponse(self._parser_responses, dumps, files)

    def get_error_dump(self, endpoint: str) -> DataFrame:
        """Fetches the failure dump of an Anaplan Import action if available
        :param endpoint: API endpoint for the anaplan action
        :type endpoint: str
        :raises Exception: Error from RequestHandler exception group
        :raises EmptyDataError: Error when data string is empty
        :raises ParserError: Source data in incorrect format
        :raises ParserWarning: Warning when parsing a file that doesn't use default parser
        :return: Failure dump for an import action
        :rtype: DataFrame
        """
        post_header = {
            "Authorization": self._conn.authorization.token_value,
            "Content-Type": "application/json",
        }

        edf = pd.DataFrame()
        dump = ""

        try:
            logger.debug("Fetching error dump")
            dump = self._handler.make_request(
                f"{endpoint}", "GET", headers=post_header
            ).text
            logger.debug("Error dump downloaded.")
        except Exception as e:
            logger.error(f"Error fetching error dump {e}", exc_info=True)

        try:
            edf = pd.read_csv(StringIO(dump))
        except (EmptyDataError, ParserError) as e:
            logger.error(f"Error loading error dump to dataframe {e}", exc_info=True)
        except ParserWarning as w:
            logger.warning(f"Warning raised while parsing csv {w}", exc_info=True)

        return edf
