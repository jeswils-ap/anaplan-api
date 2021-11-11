from typing import Union
from .ActionTask import ActionTask
from .ExportTask import ExportTask
from .ImportTask import ImportTask
from .ProcessTask import ProcessTask
from .util.Util import UnknownTaskTypeError


class TaskFactoryGenerator:
	"""Class responsible for parsing input and generating corresponding task factory"""
	_factories = {
		"117": ActionTask,
		"112": ImportTask,
		"116": ExportTask,
		"118": ProcessTask
	}

	_action_id: str

	def __init__(self, action_id: str):
		if action_id in self._factories:
			self._action_id = action_id
		else:
			raise UnknownTaskTypeError(f"Unknown action ID, must be one of {''.join(list(self._factories.keys()))}")

	def get_factory(self) -> Union[ActionTask, ExportTask, ImportTask, ProcessTask]:
		return self._factories[self._action_id]
