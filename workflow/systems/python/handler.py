import logging
from typing import Dict

from workflow.exceptions import PythonWorkflowHandlerException
from workflow.systems.base import WorkflowHandler
from workflow.util import result

logger = logging.getLogger(__name__)


class PythonWorkflowHandler(WorkflowHandler):
    def __init__(self, name, group, system, function):
        super().__init__(name, group, system)
        self._function = function

    def run(self, data: Dict):
        try:
            output = self._function(**data)
            return result(
                success=True,
                data=output
            )
        # Dedicated exception handling for workflow exceptions that should have custom message
        except PythonWorkflowHandlerException as e:
            logging.error("Error while executing workflow %s-%s: ", self.system, self.name, exc_info=e)
            return result(
                success=False,
                message=e.message,
                details=str(e)
            )
        except Exception as e:
            logging.error("Error while executing workflow %s-%s: ", self.system, self.name, exc_info=e)
            return result(
                success=False,
                message="Error while executing workflow",
                details=str(e)
            )
