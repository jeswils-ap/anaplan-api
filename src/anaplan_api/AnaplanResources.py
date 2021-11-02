#===============================================================================
# Created:        12 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    This library takes a JSON response and builds a key-value dictionary for easy traversal.
# Input:          A JSON dictionary object
# Output:         Key-value dictionary object, resource name, or resource ID
#===============================================================================
from anaplan_api.Util import ResourceNotFoundError


class AnaplanResources(object):
	resources: dict

	def __init__(self, response: dict):
		self.resources = {item['name']:item['id'] for item in response}

	#===========================================================================
	# Return resource ID based on name
	#===========================================================================
	def get_id(self, resource_name: str) -> str:
		'''
		:param resource_name: Resource name provided by user to be looked up
		'''
		try:
			return self.resources.get(resource_name)
		except:
			raise ResourceNotFoundError(f"{resource_name} not found in dictionary")
