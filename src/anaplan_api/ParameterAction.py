# ===============================================================================
# Created:        1 Nov 2021
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Base class responsible for running tasks in an Anaplan model
# ===============================================================================
import json
import logging
from time import sleep
from . import TaskResponse
from .Action import Action
from .util.Util import RequestFailedError, InvalidTaskTypeError

logger = logging.getLogger(__name__)


class ParameterAction(Action):

    def execute(self) -> TaskResponse:
        """Execute the requested import task

        :raises InvalidTaskTypeError: Task ID does not match the expected format for imports
        :raises InvalidUrlError: Provided URL is empty
        :return: Results of the requested import task
        :rtype: TaskResponse
        """
        action_id = super().action_id
        authorization = super().authorization
        post_header = {
            "Authorization": authorization,
            "Content-Type": "application/json",
        }

        if action_id[2] != "2":
            logger.error("Unsupported action type for parameterised import.")
            raise InvalidTaskTypeError(
                "Unsupported action type for parameterised import."
            )

        endpoint = f"workspaces/{super().workspace}/models/{super().model}/imports/{super().action_id}/tasks"

        task_id = ParameterAction.post_task(
            self, endpoint, post_header, ParameterAction.build_request_body(self)
        )
        return super().check_status(endpoint, task_id)

    def build_request_body(self) -> dict:
        """Generate the API request body for parametrised import task.

        :return: JSON dict with runtime mapping parameters for import task
        :rtype: dict
        """
        body = ""
        body_value = ""

        params = super().mapping_params

        if len(params) > 1:
            for key, value in params.items():
                body.join(
                    ['"entityType:"', key, '"', ',"entityType:"', value, '"', ","]
                )
            body = body[:-1]
            body_value.join(["[", body, "]"])
        else:
            for key, value in params.items():
                body_value.join(['["', key, '"', ":", '"', value, '"]'])

        return json.loads(body_value)

    def post_task(self, url: str, post_header: dict, post_body: dict) -> str:
        """Overrides parent method to send mapping parameters when executing the specified import

        :param url: URL to trigger specified import action
        :type url: str
        :param post_header: Authorization and Content-Type header headers
        :type post_header: dict
        :param post_body: JSON-formatted Mapping parameters
        :type post_body: dict
        :raises HTTPError: HTTP error code
        :raises ConnectionError: Network-related errors
        :raises SSLError: Server-side SSL certificate errors
        :raises Timeout: Request timeout errors
        :raises ConnectTimeout: Timeout error when attempting to connect
        :raises ReadTimeout: Timeout error waiting for server response
        :raises ValueError: Error locating the task ID
        :return: Import action task ID
        :rtype: str
        """
        retry_count = super().retry_count
        state = 0
        sleep_time = 10

        while True:
            try:
                run_action = (
                    super()
                    .handler.make_request(
                        url, "POST", headers=post_header, data=post_body
                    )
                    .json()
                )
                if run_action.status_code != 200 and state < retry_count:
                    sleep(sleep_time)
                    state += 1
                    sleep_time *= 1.5
                else:
                    break
            except Exception as e:
                logger.error(f"Error running action {e}", exc_info=True)
                raise Exception(f"Error running action {e}")

        if state > self.retry_count:
            raise RequestFailedError(f"Unable to execute {self._action_id}")

        if "task" not in run_action or "taskId" not in run_action["task"]:
            raise ValueError("Unable to fetch task ID.")

        return run_action["task"]["taskId"]
