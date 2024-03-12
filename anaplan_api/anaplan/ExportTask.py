from __future__ import annotations
from typing import TYPE_CHECKING
from anaplan_api.anaplan.bases.TaskFactory import TaskFactory
from .Action import Action
from .ExportParser import ExportParser
from .util.Util import TaskParameterError

if TYPE_CHECKING:
    from anaplan_api.anaplan.models.AnaplanConnection import AnaplanConnection
    from .Parser import Parser


class ExportTask(TaskFactory):
    """
    Factory to generate an Anaplan import task
    """

    @staticmethod
    def get_action(
        conn: AnaplanConnection,
        action_id: str,
        retry_count: int,
        mapping_params: dict = None,
    ) -> Action:
        """Create an initialized Action object for a requested Anaplan export

        :param conn: Contains authorization, workspace and model IDs
        :type conn: AnaplanConnection
        :param action_id: ID of the requested Anaplan export
        :type action_id:  str
        :param retry_count: Number of times to attempt to trigger the action in case of server error.
        :type retry_count: int
        :param mapping_params: Should always be None type for Export Tasks
        :type mapping_params: dict
        :raises TaskParameterError: Error when attempting to set mapping parameters for actions other than imports.
        :return: Initialized Export Action object
        :rtype: Action
        """
        if not mapping_params:
            return Action(
                conn=conn,
                action_id=action_id,
                retry_count=retry_count,
                mapping_params=mapping_params,
            )
        else:
            raise TaskParameterError("Only Anaplan imports accept mapping parameters.")

    @staticmethod
    def get_parser(conn: AnaplanConnection, results: dict, url: str) -> Parser:
        """Creates a Parser object which contains the results of the requested export task.

        :param conn: Contains authorization, workspace and model IDs
        :type conn: AnaplanConnection
        :param results: JSON array of export task results
        :type results: dict
        :param url: URL of the export task.
        :type url: str
        :return: ExportParser object with results of the export task
        :rtype: Parser
        """
        return ExportParser(conn, results, url)
