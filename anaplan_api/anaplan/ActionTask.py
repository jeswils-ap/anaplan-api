from __future__ import annotations
from typing import TYPE_CHECKING
from .bases.TaskFactory import TaskFactory
from .Action import Action
from .ActionParser import ActionParser
from .util.Util import TaskParameterError

if TYPE_CHECKING:
    from .models.AnaplanConnection import AnaplanConnection
    from .Parser import Parser


class ActionTask(TaskFactory):
    """
    Factory to generate an Anaplan action task and corresponding parser
    """

    @staticmethod
    def get_action(
        conn: AnaplanConnection,
        action_id: str,
        retry_count: int,
        mapping_params: dict = None,
    ) -> Action:
        """Get an ActionTask object

        :param conn: AnaplanConnection object containing the Workspace and Model IDs, and AuthToken object
        :type conn: AnaplanConnection
        :param action_id: ID of the Anaplan action to execute
        :type action_id: str
        :param retry_count: Number of time to attempt to retry if there's an HTTP error during execution
        :type retry_count: int
        :param mapping_params: Runtime mapping parameters for an Import action
        :type mapping_params: dict, optional
        :raises TaskParameterError: Exception if mapping parameters are provided for any other action type than import
        :return: Instantiated Action object
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
        """Get an ActionParser

        :param conn: AnaplanConnection object containing the Workspace and Model IDs, and AuthToken object
        :type conn: AnaplanConnection
        :param results: JSON object with executed task results
        :type results: dict
        :param url: URL of the executed action task
        :type url: str
        :return: Instantiated Parser object that parses and stores the results of an Anaplan task
        :rtype: Parser
        """
        return ActionParser(results, url)
