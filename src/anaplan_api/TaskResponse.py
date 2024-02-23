class TaskResponse:

    def __init__(self, results: dict, url: str):
        """
        :param results: JSON results for a task
        :type results: dict
        :param url: URL of the specified task
        :type url: str
        """
        self._results = results
        self._url = url

    def get_results(self) -> dict:
        """Get JSON results

        :return: JSON results for a task
        :rtype: dict
        """
        return self._results

    def get_url(self) -> str:
        """Get the URL of the specified task

        :return: URL of the task
        :rtype: str
        """
        return self._url
