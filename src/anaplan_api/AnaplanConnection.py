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
        """Fetch the AuthToken object.

        :return: Object with authorization and token expiry time.
        :rtype: AuthToken
        """
        return self._authorization

    def get_workspace(self) -> str:
        """Fetch the workspace ID

        :return: A 32-character string hexadecimal workspace ID.
        :rtype: str
        """
        return self._workspace_id

    def get_model(self) -> str:
        """Fetch the model ID

        :return: A 32-character string hexadecimal model ID.
        :rtype: str
        """
        return self._model_id

    def set_auth(self, authorization: AuthToken):
        """Set a new AuthToken to overwrite the object set at creation.

        :param authorization: Object with authorization and token expiry time
        :type authorization: AuthToken
        """
        self._authorization = authorization

    def set_workspace(self, workspace_id: str):
        """Set a new workspace ID

        :param workspace_id: A 32-character string hexadecimal workspace ID.
        :type workspace_id: str
        """
        self._workspace_id = workspace_id

    def set_model(self, model_id: str):
        """Set a new model ID

        :param model_id: A 32-character string hexadecimal model ID.
        :type model_id: str
        """
        self._model_id = model_id
