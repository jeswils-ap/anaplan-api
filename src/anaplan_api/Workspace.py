import json
import logging
from typing import List
import requests
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from .User import User
from .WorkspaceDetails import WorkspaceDetails

logger = logging.getLogger(__name__)


class Workspace(User):

	def get_workspaces(self) -> List[WorkspaceDetails]:
		workspace_details_list = [WorkspaceDetails]
		workspace_list = {}
		url = ''.join([super().get_url(), super().get_id(), "/workspaces"])
		authorization = super().get_conn().get_auth().get_auth_token()

		get_header = {
			"Authorization": authorization,
			"Content-Type": "application/json"
		}

		logger.info(f"Fetching workspaces for {super().get_id()}")

		try:
			workspace_list = json.loads(requests.get(url, headers=get_header, timeout=(5, 30)).text)
		except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
			logger.error(f"Error getting models list: {e}", exc_info=True)
		except ValueError as e:
			logger.error(f"Error loading model list {e}", exc_info=True)

		if 'workspaces' in workspace_list:
			workspaces = workspace_list['workspaces']
			logger.info("Finished fetching workspaces.")
			for item in workspaces:
				workspace_details_list.append(WorkspaceDetails(item))
			return workspace_details_list
		else:
			raise AttributeError("Models not found in response.")
