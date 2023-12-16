import logging
from typing import Dict

from workflow.systems.base import WorkflowHandler
from workflow.systems.lightning.client import LightningClient
from workflow.util import result

logger = logging.getLogger(__name__)


class LightningWorkflowHandler(WorkflowHandler):
    def __init__(self, name, group, system, webhook_id):
        super().__init__(name, group, system)
        self._webhook_id = webhook_id

    def run(self, data: Dict):
        try:
            with LightningClient() as c:
                trigger_response = c.trigger_workflow(self._webhook_id, data)
                if not trigger_response['success']:
                    return trigger_response
                return result(
                    success=True,
                    data=trigger_response['data']
                )
        except Exception as e:
            logging.error("Error while executing workflow %s-%s-%s: ", self.system, self.group, self.name, exc_info=e)
            return result(
                success=False,
                message="Error while executing workflow",
                details=str(e)
            )
