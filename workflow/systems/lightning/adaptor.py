import logging
from typing import Dict

from workflow.systems.base import WorkflowAdaptor
from workflow.systems.lightning.handler import LightningWorkflowHandler
from workflow.systems.lightning.client import LightningClient
from workflow.util import result

logger = logging.getLogger(__name__)


class LightningWorkflowAdaptor(WorkflowAdaptor):
    system = 'lightning'

    @classmethod
    def get_groups(cls) -> Dict:
        try:
            with LightningClient() as c:
                projects_response = c.get_projects()
                if not projects_response['success']:
                    return projects_response
                projects = cls._get_projects_from_projects_response(projects_response)
                return result(
                    success=True,
                    data={'groups': projects}
                )
        except Exception as e:
            logger.error('Error during retrieving openFN/Lightning groups', exc_info=e)
            return result(
                success=False,
                message='Error during retrieving openFN/Lightning groups',
                details=str(e)
            )

    @classmethod
    def get_workflows(cls, name: str = None, group: str = None) -> Dict:
        try:
            with LightningClient() as c:
                projects_response = c.get_projects()
                if not projects_response['success']:
                    return projects_response
                workflows = []
                for entry in projects_response['data']['data']:
                    if group and entry['attributes']['name'] != group:
                        continue

                    project_id = entry['id']
                    provision_response = c.get_provisions(project_id)
                    if not provision_response['success']:
                        return provision_response
                    workflows = workflows + cls._get_workflows_from_provision_response(provision_response, name)

                return result(
                    success=True,
                    data={'workflows': workflows}
                )
                # TODO
        except Exception as e:
            logger.error('Error during retrieving openFN/Lightning workflows', exc_info=e)
            return result(
                success=False,
                message='Error during retrieving openFN/Lightning workflows',
                details=str(e)
            )

    @classmethod
    def _get_projects_from_projects_response(cls, projects_response):
        groups = []
        for entry in projects_response['data']['data']:
            groups.append(entry['attributes']['name'])
        return groups

    @classmethod
    def _get_workflows_from_provision_response(cls, provision_response, name):
        workflows = []
        group = provision_response['data']['data']['name']
        for entry in provision_response['data']['data']['workflows']:
            if name and entry['name'] != name:
                continue

            webhook_triggers = [trigger for trigger in entry['triggers'] if trigger['type'] == 'webhook']
            if not webhook_triggers:
                raise AttributeError(
                    f'{cls.system}-{group}-{entry["name"]} have no webhook triggers. Cannot create WorkflowHandler')

            workflows.append(LightningWorkflowHandler(
                system=cls.system,
                group=group,
                name=entry['name'],
                webhook_id=webhook_triggers[0]['id']
            ))

        return workflows
