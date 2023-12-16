import logging

from typing import Dict, Iterable, Type

from workflow.systems.base import WorkflowAdaptor
from workflow.util import result

logger = logging.getLogger(__name__)


class WorkflowService:
    """
    Entry point for registering and retrieving workflow adaptors
    """

    _adaptors: Dict[str, Type[WorkflowAdaptor]] = {}

    @classmethod
    def register_system_adaptor(cls, adaptor: Type[WorkflowAdaptor]):
        if adaptor.system in cls._adaptors:
            logger.warning("Re-registration of a workflow system `%s`", adaptor.system)
        logger.info("Workflow system registered `%s`", adaptor.system)
        cls._adaptors[adaptor.system] = adaptor

    @classmethod
    def get_systems(cls) -> Dict:
        return result(success=True, data={'systems': list(cls._adaptors.keys())})

    @classmethod
    def get_groups(cls) -> Iterable[str]:
        groups = []
        for adaptor in cls._adaptors:
            adaptor_result = cls._adaptors[adaptor].get_groups()
            if not adaptor_result['success']:
                return adaptor_result
            groups = groups + adaptor_result['data']['groups']
        return result(success=True, data={'groups': list(set(groups))})

    @classmethod
    def get_workflows(cls, name: str = None, group: str = None) -> Dict:
        workflows = []
        for adaptor in cls._adaptors:
            adaptor_result = cls._adaptors[adaptor].get_workflows(name=name, group=group)
            if not adaptor_result['success']:
                return adaptor_result
            workflows = workflows + adaptor_result['data']['workflows']
        return result(success=True, data={'workflows': workflows})
