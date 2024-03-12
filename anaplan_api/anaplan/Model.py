import logging
from typing import List
from .User import User
from .models.ModelDetails import ModelDetails

logger = logging.getLogger(__name__)


class Model(User):
    def get_models(self) -> List[ModelDetails]:
        """Get list of all Anaplan model for the specified user.

        :raises Exception: Error from RequestHandler exception group.
        :raises KeyError: No models found in response.
        :return: Details for all models the user can access.
        :rtype: List[ModelDetails]
        """

        model_details_list = [ModelDetails]
        model_list = {}
        user_id = super().id
        url = "".join([super().endpoint, super().id, "/models"])
        authorization = super().conn.authorization.token_value

        get_header = {
            "Authorization": authorization,
            "Content-Type": "application/json",
        }

        logger.info(f"Fetching models for {user_id}")

        try:
            model_list = (
                super()._handler.make_request(url, "GET", headers=get_header).json()
            )
        except Exception as e:
            logger.error(f"Error getting models list: {e}", exc_info=True)
            raise Exception(f"Error getting model list {e}")

        if "models" not in model_list:
            raise KeyError("'models' not found in response")

        models = model_list["models"]
        logger.info("Finished fetching models.")
        for item in models:
            model_details_list.append(ModelDetails(item))
        return model_details_list
