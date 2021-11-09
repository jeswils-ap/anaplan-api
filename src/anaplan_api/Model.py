import json
import logging
import requests
from typing import List
from requests.exceptions import HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout
from .User import User
from .ModelDetails import ModelDetails

logger = logging.getLogger(__name__)


class Model(User):

	def get_models(self) -> List[ModelDetails]:
		model_details_list = [ModelDetails]
		model_list = {}
		url = ''.join([super().get_url(), super().get_id(), "/models"])
		authorization = super().get_conn().get_auth()

		get_header = {
			"Authorization": authorization,
			"Content-Type": "application/json"
		}

		logger.info(f"Fetching models for {super().get_id()}")

		try:
			model_list = json.loads(requests.get(url, headers=get_header, timeout=(5, 30)).text)
		except (HTTPError, ConnectionError, SSLError, Timeout, ConnectTimeout, ReadTimeout) as e:
			logger.error(f"Error getting models list: {e}")
		except ValueError as e:
			logger.error(f"Error loading model list {e}")

		if 'models' in model_list:
			models = model_list['models']
			logger.info("Finished fetching models.")
			for item in models:
				model_details_list.append(ModelDetails(item))
			return model_details_list
		else:
			raise AttributeError("Models not found in response.")
