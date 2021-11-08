from abc import ABC, abstractmethod


class AnaplanResource(ABC):
    _resource: dict

    @abstractmethod
    def __init__(self, response: dict):
        """Resource initialization"""

    @abstractmethod
    def __getitem__(self, resource_name: str):
        """Resource getter"""

    @abstractmethod
    def __len__(self):
        """Return length of the resource"""

    @abstractmethod
    def __contains__(self, resource_name: str):
        """Return True if the resource exists"""
