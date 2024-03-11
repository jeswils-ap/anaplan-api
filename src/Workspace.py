import logging
from typing import List
from .User import User
from src.models.WorkspaceDetails import WorkspaceDetails

logger = logging.getLogger(__name__)


class Workspace(User):
    def get_workspaces(self) -> List[WorkspaceDetails]:
        """
        "raises Exception" Error from RequestHandler exception group.
        :raises KeyError: Error locating Workspaces key in JSON response.
        :return: Workspace details
        :rtype: List[WorkspaceDetails]
        """
        workspace_details_list = [WorkspaceDetails]
        user_id = super().id
        url = "".join([super().endpoint, user_id, "/workspaces"])
        authorization = super().conn.authorization.token_value

        get_header = {
            "Authorization": authorization,
            "Content-Type": "application/json",
        }

        logger.info(f"Fetching workspaces for {user_id}")

        try:
            workspace_list = (
                super()._handler.make_request(url, "GET", headers=get_header).json()
            )
        except Exception as e:
            logger.error(f"Error getting workspace list: {e}", exc_info=True)
            raise Exception(f"Error getting workspaces list: {e}")

        if "workspaces" not in workspace_list:
            raise KeyError("'workspaces' not found in response")

        workspaces = workspace_list["workspaces"]
        logger.info("Finished fetching workspaces.")
        for item in workspaces:
            workspace_details_list.append(WorkspaceDetails(item))
        return workspace_details_list
