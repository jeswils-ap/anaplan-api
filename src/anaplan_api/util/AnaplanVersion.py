class AnaplanVersion:
	_api_major_version: int = 2
	_api_minor_version: int = 0

	@staticmethod
	def major():
		return AnaplanVersion._api_major_version

	@staticmethod
	def minor():
		return AnaplanVersion._api_minor_version
