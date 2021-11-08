from .ResourceParserFactory import ResourceParserFactory
from .AnaplanResourceList import AnaplanResourceList


class ResourceParserList(ResourceParserFactory):

    def get_parser(self, response: dict) -> AnaplanResourceList:
        return AnaplanResourceList(response)
