from abc import ABC, abstractmethod
from .AnaplanResource import AnaplanResource


class ResourceParserFactory(ABC):
    """
    Factory that represents parsing of a list of Anaplan resources.
    It doesn't maintain the instances it creates.
    """

    @abstractmethod
    def get_parser(self, response: dict) -> AnaplanResource:
        """Function to request Parser Object"""
