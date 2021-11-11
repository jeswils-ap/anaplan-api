from .TaskFactory import TaskFactory
from .AnaplanConnection import AnaplanConnection
from .Action import Action
from .ParameterAction import ParameterAction
from .Parser import Parser
from .ImportParser import ImportParser


class ImportTask(TaskFactory):
	"""
	Factory to generate an Anaplan import task
	"""

	@staticmethod
	def get_action(conn: AnaplanConnection, action_id: str, retry_count: int, mapping_params: dict = None) -> Action:
		if not mapping_params:
			return Action(conn=conn, action_id=action_id, retry_count=retry_count, mapping_params=mapping_params)
		elif mapping_params:
			return ParameterAction(conn=conn, action_id=action_id, retry_count=retry_count, mapping_params=mapping_params)

	@staticmethod
	def get_parser(conn: AnaplanConnection, results: dict, url: str) -> Parser:
		return ImportParser(results, url)
