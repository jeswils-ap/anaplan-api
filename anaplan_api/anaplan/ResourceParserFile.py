from anaplan_api.anaplan.bases.ResourceParserFactory import ResourceParserFactory
from anaplan_api.anaplan.models.AnaplanResourceFile import AnaplanResourceFile


class ResourceParserFile(ResourceParserFactory):

    def get_parser(self, response: dict) -> AnaplanResourceFile:
        """Get a parser object for list of Anaplan files

        :param response: JSON list of files in an Anaplan model
        :type response: dict
        :return: Initialized object containing parsed list of files.
        :rtype: AnaplanResourceFile
        """
        return AnaplanResourceFile(response)
