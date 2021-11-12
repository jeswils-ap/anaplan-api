# ===============================================================================
# Created:        1 Nov 2021
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Base class responsible for running tasks in an Anaplan model
# ===============================================================================
import logging
import requests
import json
from time import sleep
from typing import Optional
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from .AnaplanConnection import AnaplanConnection
from .util.Util import MappingParameterError

logger = logging.getLogger(__name__)


class Action(object):
    _authorization: str
    workspace: str
    model: str
    action_id: str
    retry_count: int
    mapping_params: Optional[dict]

    base_url = "https://api.anaplan.com/2/0/workspaces"
    post_body = {
        "localeName": "en_US"
    }

    def __init__(self, conn: AnaplanConnection, action_id: str, retry_count: int, mapping_params: Optional[dict]):
        self._authorization = conn.get_auth().get_auth_token()
        self.workspace = conn.get_workspace()
        self.model = conn.get_model()
        self.action_id = action_id
        self.retry_count = retry_count
        self.mapping_params = mapping_params

    def get_url(self) -> str:
        return self.base_url

    def get_body(self) -> dict:
        return self.post_body

    def get_authorization(self) -> str:
        return self._authorization

    def get_workspace(self) -> str:
        return self.workspace

    def get_model(self) -> str:
        return self.model

    def get_action(self) -> str:
        return self.action_id

    def get_retry(self) -> int:
        return self.retry_count

    def get_mapping_params(self) -> dict:
        if len(self.mapping_params) > 0:
            return self.mapping_params
        else:
            raise MappingParameterError("Unable to return empty mapping parameters.")

    def execute(self):
        authorization = self._authorization

        post_header = {
            'Authorization': authorization,
            'Content-Type': 'application/json'
        }

        url = ""

        if self.action_id[2] == "2" or self.action_id[2] == "6" or self.action_id[2] == "7" or self.action_id[2] == "8":
            if self.action_id[2] == "2":
                url = ''.join(
                    [self.base_url, "/", self.workspace, "/models/", self.model, "/imports/", self.action_id, "/tasks"])
            elif self.action_id[2] == "6":
                url = ''.join(
                    [self.base_url, "/", self.workspace, "/models/", self.model, "/exports/", self.action_id, "/tasks"])
            elif self.action_id[2] == "7":
                url = ''.join(
                    [self.base_url, "/", self.workspace, "/models/", self.model, "/actions/", self.action_id, "/tasks"])
            elif self.action_id[2] == "8":
                url = ''.join(
                    [self.base_url, "/", self.workspace, "/models/", self.model, "/processes/", self.action_id,
                     "/tasks"])

            if url is not "":
                task_id = Action.post_task(self, url, post_header)
                return Action.check_status(self, url, task_id)
            else:
                return None
        else:
            logger.error("Incorrect action ID provided!")
            return None

    def post_task(self, url: str, post_header: dict) -> str:
        state = 0
        sleep_time = 10
        run_action = None

        while True:
            try:
                run_action = requests.post(url, headers=post_header, json=self.post_body, timeout=(5, 30))
            except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
                logger.error(f"Error running action {e}", exc_info=True)
            if run_action.status_code != 200 and state < self.retry_count:
                sleep(sleep_time)
                state += 1
                sleep_time *= 1.5
            else:
                break
        if state < self.retry_count:
            task_id = json.loads(run_action.text)
            if 'task' in task_id:
                if 'taskId' in task_id['task']:
                    return task_id['task']['taskId']

    def check_status(self, url: str, task_id: str):
        """
        :param url: URL of Anaplan action
        :param task_id: Anaplan task ID for executed action
        :return:
        """

        authorization = self._authorization
        post_header = {
            'Authorization': authorization,
            'Content-Type': 'application/json'
        }
        status = ""
        status_url = ''.join([url, "/", task_id])
        get_status = None

        while True:
            try:
                get_status = json.loads(requests.get(status_url, headers=post_header, timeout=(5, 30)).text)
            except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
                logger.error(f"Error getting result for task {e}", exc_info=True)
            if 'task' in get_status:
                if 'taskState' in get_status['task']:
                    status = get_status['task']['taskState']
            if status == "COMPLETE":
                results = get_status['task']
                break
            # Wait 1 seconds before continuing loop
            sleep(1)

        return [results, status_url]
