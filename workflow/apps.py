from django.apps import AppConfig

DEFAULT_CONFIG = {
    'python_enabled': True,
    'python_example_workflow_enabled': True,
    'lightning_enabled': True,
    'lightning_url': 'http://localhost',
    'lightning_port': '4000',
    'lightning_api_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJKb2tlbiIsImlhdCI6MTY4NzM1NTQ0OCwiaXNzIjoiSm9rZW4iLCJqdGkiOiIydGxiMWxwMGhiZmR0dWhnMW8wMDAxbzEiLCJuYmYiOjE2ODczNTU0NDgsInVzZXJfaWQiOiJjNzNmOTllZi04NzE2LTRmZTgtOTE2Yi00MzdlYzVkMTlmY2UifQ.woj1PeTQsY6ryOmNzR_JEUlwjqS9_ukEcA8etoBxe7M',
}


class WorkflowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workflow'

    python_enabled = None
    python_example_workflow_enabled = None

    lightning_enabled = None
    lightning_url = None
    lightning_port = None
    lightning_api_key = None

    def ready(self):
        from core.models import ModuleConfiguration

        cfg = ModuleConfiguration.get_or_default(self.name, DEFAULT_CONFIG)
        self._load_config(cfg)
        self._set_up_workflows()

    @classmethod
    def _load_config(cls, cfg):
        """
        Load all config fields that match current AppConfig class fields, all custom fields have to be loaded separately
        """
        for field in cfg:
            if hasattr(WorkflowConfig, field):
                setattr(WorkflowConfig, field, cfg[field])

    def _set_up_workflows(self):
        from workflow.services import WorkflowService

        if self.python_enabled:
            from workflow.systems.python import PythonWorkflowAdaptor

            if self.python_example_workflow_enabled:
                PythonWorkflowAdaptor.register_workflow(
                    'example_workflow',
                    'example_group',
                    lambda args, kwargs: print(f'EXAMPLE WORKFLOW {args} {kwargs}'))
            WorkflowService.register_system_adaptor(PythonWorkflowAdaptor)

        if self.lightning_enabled:
            from workflow.systems.lightning import LightningWorkflowAdaptor
            WorkflowService.register_system_adaptor(LightningWorkflowAdaptor)
