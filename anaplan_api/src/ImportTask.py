from __future__ import annotations
from typing import TYPE_CHECKING
from anaplan_api.src.bases.TaskFactory import TaskFactory
from .Action import Action
from .ParameterAction import ParameterAction
from .ImportParser import ImportParser

if TYPE_CHECKING:
    from anaplan_api.src.models.AnaplanConnection import AnaplanConnection
    from .Parser import Parser


class ImportTask(TaskFactory):
    """Factory to generate an Anaplan import task"""

    @staticmethod
    def get_action(
        conn: AnaplanConnection,
        action_id: str,
        retry_count: int,
        mapping_params: dict = None,
    ) -> Action:
        """Get an instantiated Action object

        :param conn: Object with authentication, workspace, and model details
        :type conn: AnaplanConnection
        :param action_id: ID of the specified Anaplan action
        :type action_id: str
        :param retry_count: Number of times to attempt to retry in case of network or server error
        :type retry_count: int
        :param mapping_params: Import parameters requested at runtime
        :type mapping_params: dict
        :return:
        """
        if not mapping_params:
            return Action(
                conn=conn,
                action_id=action_id,
                retry_count=retry_count,
                mapping_params=mapping_params,
            )
        elif mapping_params:
            return ParameterAction(
                conn=conn,
                action_id=action_id,
                retry_count=retry_count,
                mapping_params=mapping_params,
            )

    @staticmethod
    def get_parser(conn: AnaplanConnection, results: dict, url: str) -> Parser:
        """Get an instantiated Parser object for import tasks

        :param conn: Object with authentication, workspace, and model details
        :type conn: AnaplanConnection
        :param results: JSON response with details of task results
        :type results: dict
        :param url: Anaplan task URL
        :type url: str
        :return: Instantiated Parser object for an import task
        :rtype: ImportParser
        """
        return ImportParser(results, url)
