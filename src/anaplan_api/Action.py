# ===============================================================================
# Created:        1 Nov 2021
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Base class responsible for running tasks in an Anaplan model
# ===============================================================================
from __future__ import annotations
from typing import Optional, TYPE_CHECKING
import logging
from time import sleep
from .util.RequestHandler import RequestHandler
from .TaskResponse import TaskResponse
from .util.AnaplanVersion import AnaplanVersion
from .util.Util import MappingParameterError, UnknownTaskTypeError, RequestFailedError

if TYPE_CHECKING:
    from .AnaplanConnection import AnaplanConnection

logger = logging.getLogger(__name__)


class Action(object):
    """
    Action represents an instance of an Anaplan action.

    :param _action_type: Mapping of action ID prefixes to the name of the action type
    :type _action_type: dict
    :param handler: Class for sending API requests
    :type handler: RequestHandler
    :param _authorization: Authorization header for API requests
    :type authorization: str
    :param workspace: ID of the Anaplan workspace
    :type workspace: str
    :param model: ID of the Anaplan model
    :type model: str
    :param action_id: ID of the Anaplan action
    :type action_id: str
    :param retry_count: Number of times to attempt to retry executing the action
    :type retry_count: int
    :param mapping_params: Parameters of import definition to be provided at runtime
    :type mapping_params: dict, option
    :param post_body: Required body when executing an Anaplan action
    :type post_body: dict
    """

    _action_type: dict = {
        "112": "/imports/",
        "116": "/exports/",
        "117": "/actions/",
        "118": "/processes/",
    }

    _handler: RequestHandler = RequestHandler(AnaplanVersion().base_url)
    _authorization: str
    _workspace: str
    _model: str
    _action_id: str
    _retry_count: int
    _mapping_params: Optional[dict]
    post_body = {"localeName": "en_US"}

    def __init__(
        self,
        conn: AnaplanConnection,
        action_id: str,
        retry_count: int,
        mapping_params: Optional[dict],
    ):
        self._authorization = conn.authorization.token_value
        self._workspace = conn.workspace
        self._model = conn.model
        self._action_id = action_id
        self._retry_count = retry_count
        self._mapping_params = mapping_params

    @property
    def handler(self) -> RequestHandler:
        """Get the post body for API requests"""
        return self._handler

    @property
    def authorization(self) -> str:
        """Get the authorization token for API requests"""
        return self._authorization

    @property
    def workspace(self) -> str:
        """Get the Anaplan workspace ID"""
        return self._workspace

    @property
    def model(self) -> str:
        """Get the Anaplan model IDn"""
        return self._model

    @property
    def action_id(self) -> str:
        """Get the Anaplan action ID"""
        return self._action_id

    @property
    def retry_count(self) -> int:
        """Get the retry count"""
        return self._retry_count

    @property
    def mapping_params(self) -> dict:
        """If defined, get the mapping parameters"""
        if len(self._mapping_params) > 0:
            return self._mapping_params
        else:
            raise MappingParameterError("Unable to return empty mapping parameters.")

    def execute(self) -> TaskResponse:
        """Triggers the specified action

        :return: TaskResponse object with the details of the completed action
        """
        authorization = self._authorization

        post_header = {
            "Authorization": authorization,
            "Content-Type": "application/json",
        }

        if self._action_id[:3] not in self._action_type:
            raise UnknownTaskTypeError(
                f"Provided action ID {self._action_id} does not match any know action type"
            )

        endpoint = f"workspaces/{self._workspace}/models/{self._model}/{self._action_type[self._action_id[:3]]}/{self._action_id}/tasks"

        task_id = self.post_task(endpoint, post_header)
        return self.check_status(endpoint, task_id)

    def post_task(self, url: str, post_header: dict) -> str:
        """Responsible for POSTing the to the Anaplan model

        :param url: URL for the action task
        :type url: str
        :param post_header: Head for the POST request, containing the authorization and content type
        :type post_header: dict
        :return: Task ID for the executed action
        """
        state = 0
        sleep_time = 10
        run_action = None

        while state < self.retry_count:
            try:
                run_action = self._handler.make_request(
                    url, "POST", data=self.post_body, headers=post_header
                ).json()
            except Exception as e:
                logger.error(f"Error running action {e}", exc_info=True)
            if run_action.status_code == 200:
                break
            logger.debug(
                f"Request failed, waiting {sleep_time} seconds before retrying."
            )
            state += 1
            sleep_time *= 1.5
            sleep(sleep_time)

        if state > self.retry_count:
            raise RequestFailedError(f"Unable to execute {self.action_id}")

        if "task" not in run_action or "taskId" not in run_action["task"]:
            raise ValueError("Unable to fetch task ID.")

        return run_action["task"]["taskId"]

    def check_status(self, url: str, task_id: str) -> TaskResponse:
        """
        Checks the status of the Anaplan task ID until complete then return the results

        :param url: URL of Anaplan action
        :param task_id: Anaplan task ID for executed action
        :return: TaskResponse object with the details of the completed action
        """

        authorization = self._authorization
        post_header = {
            "Authorization": authorization,
            "Content-Type": "application/json",
        }
        status = ""
        status_url = f"{url}/{task_id}"

        while True:
            try:
                get_status = self._handler.make_request(
                    status_url, "GET", headers=post_header
                ).json()
            except Exception as e:
                logger.error(f"Error getting result for task {e}", exc_info=True)
                raise Exception(f"Error getting result for task {e}")

            if "task" in get_status and "taskState" in get_status["task"]:
                status = get_status["task"]["taskState"]

            if status == "COMPLETE":
                results = get_status["task"]
                break
            sleep(1)  # Wait 1 second before continuing loop

        return TaskResponse(results, status_url)
