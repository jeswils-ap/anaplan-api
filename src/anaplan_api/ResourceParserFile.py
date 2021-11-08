from .ResourceParserFactory import ResourceParserFactory
from .AnaplanResourceFile import AnaplanResourceFile


class ResourceParserFile(ResourceParserFactory):

    def get_parser(self, response: dict) -> AnaplanResourceFile:
        return AnaplanResourceFile(response)
