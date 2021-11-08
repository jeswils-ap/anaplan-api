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
from .AnaplanConnection import AnaplanConnection
from .Action import Action

logger = logging.getLogger(__name__)


class ParameterAction(Action):
	authorization: str
	workspace: str
	model: str
	action_id: str
	retry_count: int
	request_params: dict

	def __init__(self, conn: AnaplanConnection, action_id: str, retry_count: int, request_params: dict):
		self.authorization = conn.get_auth()
		self.workspace = conn.get_workspace()
		self.model = conn.get_model()
		self.action_id = action_id
		self.retry_count = retry_count
		self.request_params = request_params

	def execute(self):
		url = ""
		authorization = super().get_authorization()
		post_header = {
						'Authorization': authorization,
						'Content-Type': 'application/json'
				}

		if self.action_id[2] == "2" or self.action_id[2] == "6" or self.action_id[2] == "7" or self.action_id[2] == "8":
			if self.action_id[2] == "2":
				url = ''.join([super().get_url(), "/", super().get_workspace(), "/models/", super().get_model(), "/imports/", super().get_action(), "/tasks"])
			elif self.action_id[2] == "6":
				url = ''.join([super().get_url(), "/", super().get_workspace(), "/models/", super().get_model(), "/exports/", super().get_action(), "/tasks"])
			elif self.action_id[2] == "7":
				url = ''.join([super().get_url(), "/", super().get_workspace(), "/models/", super().get_model(), "/actions/", super().get_action(), "/tasks"])
			elif self.action_id[2] == "8":
				url = ''.join([super().get_url(), "/", super().get_workspace(), "/models/", super().get_model(), "/processes/", super().get_action(), "/tasks"])

			if url is not "":
				task_id = ParameterAction.post_task(self, url, post_header, ParameterAction.build_request_body(self))
				return super().check_status(url, task_id)
			else:
				return None
		else:
			logger.error("Incorrect action ID provided!")
			return None

	def build_request_body(self) -> dict:
		body = ""
		body_value = ""

		params = self.request_params
		
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
		state = 0
		sleep_time = 10
			
		while True:
			try:
				run_action = requests.post(url, headers=post_header, json=post_body, timeout=(5, 30))
				if run_action.status_code != 200 and state < self.retry_count:
					sleep(sleep_time)
					state += 1
					sleep_time *= 1.5
				else:
					break
			except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
				logger.error(f"Error running action {e}")
		if state < self.retry_count:
			task_id = json.loads(run_action.text)
			if 'task' in task_id:
				if 'taskId' in task_id['task']:
					return task_id['task']['taskId']
