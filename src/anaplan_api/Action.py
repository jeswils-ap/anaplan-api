#===============================================================================
# Created:        1 Nov 2021
# @author:        Jesse Wilson (Anaplan Asia Pte Ltd)
# Description:    Base class responsible for running tasks in an Anaplan model
#===============================================================================
import requests, json
from typing import List
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from anaplan_api.AnaplanConnection import AnaplanConnection


class Action(object):
	authorization: str
	workspace: str
	model: str
	action_id: str
	retry_count: int

	base_url = "https://api.anaplan.com/2/0/workspaces"
	post_body = {
					"localeName": "en_US"
			}

	def __init__(self, conn: AnaplanConnection, action_id: str, retry_count: int):
		self.authorization = conn.get_auth()
		self.workspace = conn.get_workspace()
		self.model = conn.get_model()
		self.action_id = action_id
		self.retry_count = retry_count

	def get_url(self) -> str:
		return self.base_url

	def get_body(self) -> dict:
		return self.post_body

	def get_authorization(self) -> str:
		return self.authorization

	def get_workspace(self) -> str:
		return self.workspace

	def get_model(self) -> str:
		return self.model

	def get_action(self) -> str:
		return self.action_id

	def get_retry(self) -> int:
		return self.retry_count

	def execute(self) -> List[str]:
		authorization = self.authorization

		post_header = {
						'Authorization': authorization,
						'Content-Type': 'application/json'
				}

		if self.action_id[2] == "2" or self.action_id[2] == "6" or self.action_id[2] == "7" or self.action_id[2] == "8":
			if self.action_id[2] == "2":
				url = ''.join([self.base_url, "/", self.workspace, "/models/", self.model, "/imports/", self.action_id, "/tasks"])
			elif self.action_id[2] == "6":
				url = ''.join([self.base_url, "/", self.workspace, "/models/", self.model, "/exports/", self.action_id, "/tasks"])
			elif self.action_id[2] == "7":
				url = ''.join([self.base_url, "/", self.workspace, "/models/", self.model, "/actions/", self.action_id, "/tasks"])
			elif self.action_id[2] == "8":
				url = ''.join([self.base_url, "/", self.workspace, "/models/", self.model, "/processes/", self.action_id, "/tasks"])

			if url is not "":
				task_id = Action.post_task(self, url, post_header)
				return Action.check_status(url, task_id, post_header)
			else:
				return None
		else:
			logger.error("Incorrect action ID provided!")
			return None

	def post_task(self, url: str, post_header: dict):
		state = 0
		sleepTime = 10
			
		while True:
			try:
				run_action = requests.post(url, headers=post_header, json=self.post_body, timeout=(5,30))
			except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
				logger.error(f"Error running action {e}")
			if run_action.status_code != 200 and state < self.retry_count:
				sleep(sleepTime)
				state += 1
				sleepTime *= 1.5
			else:
				break
		if state < self.retry_count:
			task_id = json.loads(run_action.text)
			if 'task' in task_id:
				if 'taskId' in task_id['task']:
					return task_id['task']['taskId']

	def check_status(url: str, task_id: str, post_header: dict):
		'''
		@param url: Anaplan task URL
		@param task_id: ID of the Anaplan task executed
		@param post_header: Authorization header value
		'''
		status = ""
		status_url = ''.join([url, "/", task_id])

		while True:
			try:
				get_status = json.loads(requests.get(status_url, headers=post_header, timeout=(5,30)).text)
			except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
				logger.error(f"Error getting result for task {e}")
			if 'task' in get_status:
				if 'taskState' in get_status['task']:
					status = get_status['task']['taskState']
			if status == "COMPLETE":
				results = get_status['task']
				break
			#Wait 1 seconds before continuing loop
			sleep(1)
		
		return [results, status_url]
