#===============================================================================
# Created:        13 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Class to contain Anaplan connection details required for all API calls
# Input:          Authorization header string, workspace ID string, and model ID string
# Output:         None
#===============================================================================
from dataclasses import dataclass, field
from anaplan_api.AuthToken import AuthToken


@dataclass(frozen=True, eq=True)
class AnaplanConnection(object):
	'''
	Instance of connection to an Anaplan model. Only one instance may exist for a model ID.
	Contains AuthToken for the session, Anaplan workspace and model IDs.
	'''
	authorization: AuthToken
	workspaceGuid: str
	modelGuid: str = field(compare=True)

	def get_auth(self):
		return self.authorization

	def get_workspace(self):
		return self.workspaceGuid

	def get_model(self):
		return self.modelGuid

	def set_auth(self, authorization):
		self.authorization = authorization

	def set_workspace(self, workspaceGuid):
		self.workspaceGuid = workspaceGuid

	def set_model(self, modelGuid):
		self.modelGuid = modelGuid