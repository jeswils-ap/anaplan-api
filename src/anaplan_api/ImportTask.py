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
			return Action(conn, action_id, retry_count)
		elif mapping_params:
			return ParameterAction(conn, action_id, retry_count, mapping_params)

	@staticmethod
	def get_parser(conn: AnaplanConnection, results: dict, url: str) -> Parser:
		return ImportParser(results, url)
