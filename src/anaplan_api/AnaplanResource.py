from abc import ABC, abstractmethod

class AnaplanResource(ABC):
    """Represents a list of a particular resource from Anaplan.

    :param _resource: List of items for a requested Anaplan resource
    :type _resource: dict
    """
    _resource: dict

    @abstractmethod
    def __init__(self):
        """Resource initialization"""

    def __str__(self):
        """Print all elements of the resource"""

    @abstractmethod
    def __getitem__(self, resource_name: str):
        """Resource getter"""

    @abstractmethod
    def __len__(self):
        """Return length of the resource"""

    @abstractmethod
    def __contains__(self, resource_name: str):
        """Return True if the resource exists"""
