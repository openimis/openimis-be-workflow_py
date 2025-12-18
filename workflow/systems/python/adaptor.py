import logging
from typing import Iterable, Dict, Callable, Any, List

from workflow.systems.base import WorkflowAdaptor, WorkflowHandler
from workflow.systems.python.handler import PythonWorkflowHandler
from workflow.util import result

logger = logging.getLogger(__name__)


class PythonWorkflowAdaptor(WorkflowAdaptor):
    """
        Simple python function store. Converts workflow metadata into instance of PythonWorkflowHandler.
        Storage:
        {
            "group": {
                "name": {
                    "function": workflow_function
                }
            }
        }
    """

    _register: Dict = {}
    system = 'python'

    @classmethod
    def get_groups(cls) -> Iterable[str]:
        groups = list(cls._register.keys())
        return result(success=True, data={'groups': groups})

    @classmethod
    def get_workflows(cls, name: str = None, group: str = None) -> Iterable[WorkflowHandler]:
        try:
            workflows = [
                PythonWorkflowHandler(reg_name, reg_group, cls.system, cls._register[reg_group][reg_name])
                for reg_group in cls._register if not group or reg_group == group
                for reg_name in cls._register[reg_group] if not name or reg_name == name
            ]
            return result(success=True, data={'workflows': workflows})
        except Exception as e:
            logger.error("Error while getting groups from %s", cls.system, exc_info=e)
            return result(success=False, message="Error while getting groups from python adaptor", details=str(e))

    @classmethod
    def register_workflow(cls, name: str, group: str, function: Callable[[List[Any], Dict[str, Any]], Any]):
        if group not in cls._register:
            cls._register[group] = {}

        if name in cls._register[group]:
            logger.warning("Re-registration of a workflow `%s-%s-%s`", cls.system, group, name)

        logger.info("Workflow registered `%s-%s-%s`", cls.system, group, name)
        cls._register[group][name] = function
