from .TaskFactory import TaskFactory
from .AnaplanConnection import AnaplanConnection
from .Action import Action
from .Parser import Parser
from .ActionParser import ActionParser


class ActionTask(TaskFactory):
	"""
	Factory to generate an Anaplan action task
	"""

	@staticmethod
	def get_action(conn: AnaplanConnection, action_id: str, retry_count: int) -> Action:
		return Action(conn, action_id, retry_count)

	@staticmethod
	def get_parser(conn: AnaplanConnection, results: dict, url: str) -> Parser:
		return ActionParser(results, url)
