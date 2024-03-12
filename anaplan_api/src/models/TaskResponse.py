from dataclasses import dataclass


@dataclass
class TaskResponse:
    _results: dict
    _url: str

    @property
    def results(self) -> dict:
        """Get JSON results

        :return: JSON results for a task
        :rtype: dict
        """
        return self._results

    @property
    def url(self) -> str:
        """Get the URL of the specified task

        :return: URL of the task
        :rtype: str
        """
        return self._url
