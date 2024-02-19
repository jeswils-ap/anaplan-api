from dataclasses import dataclass


@dataclass
class AnaplanVersion:
	_api_major_version: int = 2
	_api_minor_version: int = 0

	@property
	def major(self):
		return self._api_major_version

	@property
	def minor(self):
		return self._api_minor_version

	@property
	def base_url(self):
		return f"https://api.anaplan.com/{self._api_major_version}/{self._api_minor_version}/"
