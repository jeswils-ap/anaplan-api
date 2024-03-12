from dataclasses import dataclass

from anaplan_api.anaplan.util.strtobool import strtobool


@dataclass
class WorkspaceDetails(object):
    _model_details: dict
    _id: str
    _name: str
    _active: bool
    _allowance: float

    def __init__(self, details: dict):
        """
        :param details: JSON workspace details
        """
        self._model_details = details
        self._id = details["id"]
        self._name = details["name"]
        self._active = strtobool(str(details["active"]))
        self._allowance = float(details["sizeAllowance"]) / (1024**2)
        self._current_size = float(details["currentSize"]) / (1024**2)

    def __str__(self) -> str:
        """
        :return: Friendly workspace details
        :rtype: str
        """
        return (
            f"Workspace name: {self._name}, ID: {self._id}, Model state: {self._active}, "
            f"workspace allowance: {self._allowance}"
        )
