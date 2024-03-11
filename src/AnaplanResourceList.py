# ===============================================================================
# Created:        12 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    This library takes a JSON response and builds a key-value dictionary for easy traversal.
# Input:          A JSON dictionary object
# Output:         Key-value dictionary object, resource name, or resource ID
# ===============================================================================
import json
from .AnaplanResource import AnaplanResource
from .util.Util import ResourceNotFoundError


class AnaplanResourceList(AnaplanResource):
    """Represents a dictionary of Anaplan resources by name with ID as the value
    :param _raw_response: Raw JSON response from the server
    :type _raw_response: dict
    :param _resource: List of items for a requested Anaplan resource
    :type _resource: dict
    """
    _raw_response: dict
    _resources: dict

    def __init__(self, response: dict):
        """Build dictionary of resources with name as key and ID as value.

        :param response: JSON response containing all items of a requested type in the Anaplan model
        :type response: dict
        """
        self._raw_response = response
        self._resources = {item["name"]: item["id"] for item in response}

    def __str__(self) -> str:
        """Get all values from the dictionary

        :return: All items in the JSON dictionary in string format
        :rtype: str
        """
        return json.dumps(self._resources)

    def __iter__(self):
        for key, value in self._resources.items():
            if key:
                yield key, value

    def __getitem__(self, resource_name: str) -> str:
        """Get the ID of a requested resource

        :param resource_name: Resource name provided by user to be looked up
        :type resource_name: str
        :raises ResourceNotFoundError: Error if the requested key does not exist
        :return: ID of the requested resource
        :rtype: str
        """
        try:
            return self._resources[resource_name]
        except ResourceNotFoundError:
            raise ResourceNotFoundError(f"{resource_name} not found in dictionary")

    def __len__(self) -> int:
        """Get number of items in the dictionary"""
        return len(self._resources)

    def __contains__(self, resource_name: str) -> bool:
        """Check if the dictionary contains the specified ID

        :param resource_name: Name of the resource to look for
        :type resource_name: str
        :return: True if requested resource ID exists in dictionary
        :rtype: bool
        """
        return True if resource_name in self._resources else False
