from __future__ import annotations
from typing import TYPE_CHECKING
from .TaskFactory import TaskFactory
from .Action import Action
from .ProcessParser import ProcessParser
from .util.Util import TaskParameterError

if TYPE_CHECKING:
    from .AnaplanConnection import AnaplanConnection
    from .Parser import Parser


class ProcessTask(TaskFactory):
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
        """Get an initialized object for executing the specified process

        :param conn: Object with authentication, workspace, and model details
        :type conn: AnaplanConnection
        :param action_id: ID for the Anaplan process to execute
        :type action_id: str
        :param retry_count: Number of time to attempt to retry request in case of network or server error
        :type retry_count: int
        :param mapping_params: Should be empty for Process tasks
        :type mapping_params: None
        :raises TaskParameterError: Error if mapping parameters are provided for action other than Import
        :return: Initialized object for executing a process
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
        """Get a parser object for process task results

        :param conn: Object with authentication, workspace, and model details
        :type conn: AnaplanConnection
        :param results: JSON results of the specified process task
        :type results: dict
        :param url: URL of the specified process task
        :type url: str
        :return: Initialized object for parsing task results
        :rtype: Parser
        """
        return ProcessParser(conn, results, url)
