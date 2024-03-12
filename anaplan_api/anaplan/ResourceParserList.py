from anaplan_api.anaplan.bases.ResourceParserFactory import ResourceParserFactory
from anaplan_api.anaplan.models.AnaplanResourceList import AnaplanResourceList


class ResourceParserList(ResourceParserFactory):

    def get_parser(self, response: dict) -> AnaplanResourceList:
        """Get a parser object for lists of non-file resources in an Anaplan model

        :param response: JSON list of a specified resource in an Anaplan model
        :type response: dict
        :return: Initialized object containing parsed list of the specified resource
        :rtype: AnaplanResourceList
        """
        return AnaplanResourceList(response)
