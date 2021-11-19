# ===============================================================================
# Created:        13 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Class to contain Anaplan connection details required for all API calls
# Input:          Authorization header string, workspace ID string, and model ID string
# Output:         None
# ===============================================================================
from dataclasses import dataclass
from .AuthToken import AuthToken


@dataclass()
class AnaplanConnection(object):
    """
    AnaplanConnection object stores AuthToken, workspace and model IDs.
    Model ID must be unique.
    """
    _authorization: AuthToken
    _workspace_id: str
    _model_id: str

    def __init__(self, authorization, workspace_id, model_id):
        self._authorization = authorization
        self._workspace_id = workspace_id
        self._model_id = model_id

    def get_auth(self) -> AuthToken:
        return self._authorization

    def get_workspace(self) -> str:
        return self._workspace_id

    def get_model(self) -> str:
        return self._model_id

    def set_auth(self, authorization):
        self._authorization = authorization

    def set_workspace(self, workspace_id):
        self._workspace_id = workspace_id

    def set_model(self, model_id):
        self._model_id = model_id
