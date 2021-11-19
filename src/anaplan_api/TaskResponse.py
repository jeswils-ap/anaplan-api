class TaskResponse:

	def __init__(self, results: dict, url: str):
		self._results = results
		self._url = url

	def get_results(self) -> dict:
		return self._results

	def get_url(self) -> str:
		return self._url
