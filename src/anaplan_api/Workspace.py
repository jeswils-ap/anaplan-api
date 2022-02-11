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
		"""
		:raises HTTPError: HTTP error code
		:raises ConnectionError: Network-related errors
		:raises SSLError: Server-side SSL certificate errors
		:raises Timeout: Request timeout errors
		:raises ConnectTimeout: Timeout error when attempting to connect
		:raises ReadTimeout: Timeout error waiting for server response
		:raises ValueError: Error loading text response to JSON
		:raises KeyError: Error locating Workspaces key in JSON response.
		:return: Workspace details
		:rtype: List[WorkspaceDetails]
		"""
		workspace_details_list = [WorkspaceDetails]
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
			logger.error(f"Error getting workspace list: {e}", exc_info=True)
			raise Exception(f"Error getting workspaces list: {e}")
		except ValueError as e:
			logger.error(f"Error loading workspace list {e}", exc_info=True)
			raise ValueError(f"Error loading workspace list {e}")

		if 'workspaces' in workspace_list:
			workspaces = workspace_list['workspaces']
			logger.info("Finished fetching workspaces.")
			for item in workspaces:
				workspace_details_list.append(WorkspaceDetails(item))
			return workspace_details_list
		else:
			raise AttributeError("Workspaces not found in response.")
