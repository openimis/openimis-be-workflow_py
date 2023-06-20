from django.apps import AppConfig

DEFAULT_CONFIG = {
    'lightning_enabled': False,
    'lightning_url': 'http://localhost',
    'lightning_port': '4000',
    'lightning_api_key': '<api key>',
}


class WorkflowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workflow'

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
        from workflow.systems.python import PythonWorkflowAdaptor
        PythonWorkflowAdaptor.register_workflow(
            'example_workflow',
            'example_group',
            lambda args, kwargs: print(f'EXAMPLE WORKFLOW {args} {kwargs}')
        )
        WorkflowService.register_system_adaptor(PythonWorkflowAdaptor)


        if self.lightning_enabled:
            from workflow.systems.lightning import LightningWorkflowAdaptor
            WorkflowService.register_system_adaptor(LightningWorkflowAdaptor)
