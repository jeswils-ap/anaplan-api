# ===============================================================================
# Created:        13 Sep 2018
# @author:        Jesse Wilson
# Description:    Class to contain Anaplan connection details required for all API calls
# Input:          Authorization header string, workspace ID string, and model ID string
# Output:         None
# ===============================================================================
from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from anaplan_api.anaplan.models.AuthToken import AuthToken


@dataclass
class AnaplanConnection(object):
    """
    AnaplanConnection object stores AuthToken, workspace and model IDs.
    Model ID must be unique.
    """

    _authorization: AuthToken
    _workspace_id: str
    _model_id: str

    @property
    def authorization(self) -> AuthToken:
        """Fetch the AuthToken object.

        :return: Object with authorization and token expiry time.
        :rtype: AuthToken
        """
        return self._authorization

    @authorization.setter
    def authorization(self, new_authorization: AuthToken) -> None:
        """Set a new model ID

        :param new_authorization: Object with authorization and token expiry time.
        :type new_authorization: AuthToken
        """
        self.authorization = new_authorization

    @property
    def workspace(self) -> str:
        """Fetch the workspace ID

        :return: A 32-character string hexadecimal workspace ID.
        :rtype: str
        """
        return self._workspace_id

    @workspace.setter
    def workspace(self, new_workspace_id: str) -> None:
        """Set a new workspace ID

        :param new_workspace_id: A 32-character string hexadecimal workspace ID.
        :type new_workspace_id: str
        """
        self._workspace_id = new_workspace_id

    @property
    def model(self) -> str:
        """Fetch the model ID

        :return: A 32-character string hexadecimal model ID.
        :rtype: str
        """
        return self._model_id

    @model.setter
    def model(self, new_model_id) -> None:
        """Set a new model ID

        :param new_model_id: A 32-character string hexadecimal model ID.
        :type new_model_id: str
        """
        self._model_id = new_model_id
