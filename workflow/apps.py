from django.apps import AppConfig

from core.rights_declaration import RightsDeclaration

MODULE_NAME = "workflow"


# Rights, by entity then by action. The module has only one entity, `workflow` - a
# process exposed by an external system (in-process python, or Lightning over HTTP) -
# and a single action, reading their list: nothing is created and nothing is executed
# through this GraphQL schema, `resolve_workflow` merely lists what the adapters
# declare.
#
# 210001: the first right of this module, in a fresh block. `resolve_workflow` required
# nothing - not even authentication - and its `_check_permissions`, never called,
# borrowed the individual module's search right, which tied the visibility of workflows
# to an unrelated entity.
#
# `workflow.view_workflow` is purely declarative, more so than elsewhere: this module
# has no django model at all (`models.py` is empty, `migrations/` holds only its
# __init__), the workflows coming from `WorkflowService.get_workflows`. The name
# therefore follows the `app_label.view_<model>` convention with the model this module
# *would* have if it had one - `Workflow`, the name the GraphQL type already carries
# (`WorkflowGQLType`) and the prefix of the catalogue key
# (`workflow.workflow_search`). The app_label `workflow` is this AppConfig's, and that
# one is real.
DJANGO_PERMS = {
    "workflow": {
        "query": ("workflow.view_workflow", 210001),
    },
}

_PERM_CFG = {
    "gql_workflow_search_perms": ("workflow", "query"),
}

RIGHTS = RightsDeclaration(MODULE_NAME, DJANGO_PERMS, _PERM_CFG)

perms = RIGHTS.perms
django_perms = RIGHTS.django_perm_names
configured_perms = RIGHTS.configured
require = RIGHTS.require


# No `get_rights` on a model here, and that is not an oversight: this module has no
# model at all. The access point to the configured value is `configured_perms`, called
# from `workflow.schema.Query._check_permissions`.
DEFAULT_CONFIG = {
    'python_enabled': True,
    'python_example_workflow_enabled': True,
    'lightning_enabled': False,
    'lightning_url': 'http://localhost',
    'lightning_port': '4000',
    'lightning_api_key': '<api key>',
}


class WorkflowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = MODULE_NAME

    # Rights: constants, no longer overridable. They go neither through DEFAULT_CFG
    # nor through ready(): `ModuleConfiguration.get_or_default` now ignores any
    # `_perms` key stored in the database.
    gql_workflow_search_perms = RIGHTS.perms("workflow", "query")

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
                    lambda data: print(f'EXAMPLE WORKFLOW {data}'))
            WorkflowService.register_system_adaptor(PythonWorkflowAdaptor)

        if self.lightning_enabled:
            from workflow.systems.lightning import LightningWorkflowAdaptor
            WorkflowService.register_system_adaptor(LightningWorkflowAdaptor)
