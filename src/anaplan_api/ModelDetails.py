from dataclasses import dataclass


@dataclass()
class ModelDetails(object):
    _model_details: dict
    _id: str
    _state: str
    _name: str
    _workspace_id: str
    _workspace_name: str

    def __init__(self, details: dict):
        """
        :param details: JSON response with details for a specific model
        :type details: dict
        """
        self._model_details = details
        self._id = details["id"]
        self._state = details["activeState"]
        self._name = details["name"]
        self._workspace_id = details["currentWorkspaceId"]
        self._workspace_name = details["currentWorkspaceName"]

    def __str__(self) -> str:
        """Return friendly model details

        :return: Friendly model details
        :rtype: str
        """
        return (
            f"Model name: {self._name}, ID: {self._id}, Model state: {self._state}, "
            f"Current workspace: {self._workspace_id}, workspace name: {self._workspace_name}"
        )
