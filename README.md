# openIMIS Backend workflow reference module
This repository holds the files of the openIMIS Backend Workflow reference module.
It is dedicated to be deployed as a module of [openimis-be_py](https://github.com/openimis/openimis-be_py).

## Services
- Workflow service
  - register
  - get systems/groups/workflows

## Registering workflow systems
Workflow service can be extended with custom adaptors to integrate with new workflow systems. Any adaptor have to 
extend ``workflow.systems.base.WorkflowAdaptor`` and return triggers as implementations of 
``workflow.systems.base.WorkflowHandler``.
```Python
WorkflowService.register_system_adaptor(CustomWorkflowAdaptor)
```

## Querying workflows
Querying available workflows can be done using ``WorkflowService.get_workflows`` service. All registered workflow systems
have to implement filtering workflows by group and name.
```Python
workflows_result = WorkflowService.get_workflows(group='default', name='example')
if workflows_result['success']:
    workflow_handlers = workflows_result['data']['workflows']
```

## Executing workflows
Workflow handlers are self contained triggers for a specific workflow in a given system. the ``WorkflowHandler.run``
method allows perform a workflow run with a given payload.
```Python
payload = { ... }
result = handler.run(payload)
```
Depending on the system, workflow runs can be synchronous and will return result of the workflow, or asynchronous and 
will return necessary info to check workflow status in a given workflow system.

