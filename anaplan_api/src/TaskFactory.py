from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from anaplan_api.src.models.AnaplanConnection import AnaplanConnection
    from .Action import Action
    from .Parser import Parser


class TaskFactory(ABC):
    """
    Factory that represents execution and parsing of a task.
    It doesn't maintain the instances it creates.
    """

    @staticmethod
    @abstractmethod
    def get_action(
        conn: AnaplanConnection,
        action_id: str,
        retry_count: int,
        mapping_params: dict = None,
    ) -> Action:
        """Function to request Action object"""

    @staticmethod
    @abstractmethod
    def get_parser(conn: AnaplanConnection, results: dict, url: str) -> Parser:
        """Function to request Parser Object"""
