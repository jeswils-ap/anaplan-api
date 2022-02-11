# ===============================================================================
# Created:        1 Nov 2021
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Base class responsible for running tasks in an Anaplan model
# ===============================================================================
import requests
import json
import logging
from time import sleep
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout

from . import TaskResponse
from .Action import Action
from .util.Util import InvalidUrlError, InvalidTaskTypeError

logger = logging.getLogger(__name__)


class ParameterAction(Action):

	def execute(self) -> TaskResponse:
		"""Execute the requested import task

		:raises InvalidTaskTypeError: Task ID does not match the expected format for imports
		:raises InvalidUrlError: Provided URL is empty
		:return: Results of the requested import task
		:rtype: TaskResponse
		"""
		action_id = super().get_action()
		authorization = super().get_authorization()
		post_header = {
						'Authorization': authorization,
						'Content-Type': 'application/json'
				}

		if action_id[2] == "2":
			url = ''.join([super().get_url(), "/", super().get_workspace(), "/models/", super().get_model(),
			               "/imports/", super().get_action(), "/tasks"])

			if url is not "":
				task_id = ParameterAction.post_task(self, url, post_header, ParameterAction.build_request_body(self))
				return super().check_status(url, task_id)
			else:
				raise InvalidUrlError("URL must not be empty.")
		else:
			logger.error("Incorrect action ID provided!")
			raise InvalidTaskTypeError("Incorrect action ID provided!")

	def build_request_body(self) -> dict:
		"""Generate the API request body for parametrised import task.

		:return: JSON dict with runtime mapping parameters for import task
		:rtype: dict
		"""
		body = ""
		body_value = ""

		params = super().get_mapping_params()

		if len(params) > 1:
			for key, value in params.items():
				body.join(["\"entityType:\"", key, "\"", ",\"entityType:\"", value, "\"", ","])
			body = body[:-1]
			body_value.join(["[", body, "]"])
		else:
			for key, value in params.items():
				body_value.join(["[\"", key, "\"", ":", "\"", value, "\"]"])

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
		retry_count = super().get_retry()
		state = 0
		sleep_time = 10

		while True:
			try:
				run_action = requests.post(url, headers=post_header, json=post_body, timeout=(5, 30))
				if run_action.status_code != 200 and state < retry_count:
					sleep(sleep_time)
					state += 1
					sleep_time *= 1.5
				else:
					break
			except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
				logger.error(f"Error running action {e}", exc_info=True)
				raise Exception(f"Error running action {e}")
		if state < retry_count:
			task_id = json.loads(run_action.text)
			if 'task' in task_id:
				if 'taskId' in task_id['task']:
					return task_id['task']['taskId']
				else:
					raise ValueError("taskId not found in response")
			else:
				raise ValueError("task not found in response")
