# ===============================================================================
# Created:        12 Sep 2018
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    This library takes a JSON response and builds a key-value dictionary for easy traversal.
# Input:          A JSON dictionary object
# Output:         Key-value dictionary object, resource name, or resource ID
# ===============================================================================
import json
from ..bases.AnaplanResource import AnaplanResource
from ..util.Util import ResourceNotFoundError


class AnaplanResourceFile(AnaplanResource):
    """Represents a dictionary of Anaplan files by ID and corresponding number of chunks that make up the file
    :param _raw_response: Raw JSON response from the server
    :type _raw_response: dict
    :param _resource: List of items for a requested Anaplan resource
    :type _resource: dict
    """

    _raw_response: dict
    _resources: dict

    def __init__(self, response: dict):
        """Build dictionary of files with ID as key and chunk count as value.

        :param response: JSON response containing all files in the Anaplan model
        :type response: dict
        """
        self._raw_response = response
        self._resources = {item["id"]: item["chunkCount"] for item in response}

    def __str__(self) -> str:
        """Get all values from the dictionary

        :return: JSON dictionary in string format.
        :rtype: str
        """
        return json.dumps(self._resources)

    def __getitem__(self, resource_id: str) -> int:
        """
        :param resource_id: ID of the file
        :type resource_id: str
        :raises ResourceNotFoundError: Error if the requested key does not exist
        :return: Number of chunks for the requested file
        :rtype: int
        """
        try:
            return self._resources[resource_id]
        except ResourceNotFoundError:
            raise ResourceNotFoundError(f"{resource_id} not found in dictionary")

    def __len__(self) -> int:
        """Get number of items in the dictionary

        :return: Number of items in the dictionary
        :rtype: int
        """
        return len(self._resources)

    def __contains__(self, resource_id: str) -> bool:
        """Check if the dictionary contains the specified ID

        :param resource_id: ID of the resource to look for
        :type resource_id: str
        :return: True if requested resource ID exists in dictionary
        :rtype: bool
        """
        return True if resource_id in self._resources else False
