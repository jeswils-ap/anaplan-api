from dataclasses import dataclass
from typing import Union


@dataclass()
class AnaplanRequest:
	_url: str
	_header: dict
	_body: Union[dict, str]

	def __init__(self, url: str, header: dict, body: Union[dict, str] = None):
		self._url = url
		self._header = header
		if body:
			self._body = body

	def get_url(self):
		return self._url

	def get_header(self):
		return self._header

	def get_body(self):
		if self._body:
			return self._body
		else:
			raise ValueError("Request body is empty")
