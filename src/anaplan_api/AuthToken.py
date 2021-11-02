#===============================================================================
# Created:        20 Oct 2021
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Class to contain Anaplan Auth Token details required for all API calls
# Input:          Auth token value and expiry
# Output:         None
#===============================================================================
from dataclasses import dataclass


@dataclass
class AuthToken(object):
	'''
	classdocs
	'''
	token_value: str
	token_expiry: str

	def get_auth_token(self):
		return self.token_value

	def set_auth_token(self, token_value):
		self.token_value = token_value

	def get_token_expiry(self):
		return self.token_expiry

	def set_token_expiry(self, token_expiry):
		self.token_expiry = token_expiry
