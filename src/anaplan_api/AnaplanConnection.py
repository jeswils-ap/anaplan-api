# ===============================================================================
# Created:        13 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Class to contain Anaplan connection details required for all API calls
# Input:          Authorization header string, workspace ID string, and model ID string
# Output:         None
# ===============================================================================
from dataclasses import dataclass, field
from .AuthToken import AuthToken


@dataclass()
class AnaplanConnection(object):
    """
    AnaplanConnection object stores AuthToken, workspace and model IDs.
    Model ID must be unique.
    """
    _authorization: AuthToken
    _workspace_guid: str
    _model_guid: str = field()

    def __init__(self, authorization, workspace_guid, model_guid):
        self._authorization = authorization
        self._workspace_guid = workspace_guid
        self._model_guid = model_guid

    def get_auth(self):
        return self._authorization

    def get_workspace(self):
        return self._workspace_guid

    def get_model(self):
        return self._model_guid

    def set_auth(self, authorization):
        self._authorization = authorization

    def set_workspace(self, workspace_guid):
        self._workspace_guid = workspace_guid

    def set_model(self, model_guid):
        self._model_guid = model_guid
