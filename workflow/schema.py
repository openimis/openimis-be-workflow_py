import graphene
from django.contrib.auth.models import AnonymousUser

from workflow.apps import WorkflowConfig
from workflow.gql_queries import WorkflowGQLType
from workflow.services import WorkflowService


class Query:
    workflow = graphene.Field(
        graphene.List(WorkflowGQLType),
        name=graphene.Argument(graphene.String, required=False),
        group=graphene.Argument(graphene.String, required=False),
    )

    def resolve_workflow(self, info, **kwargs):
        Query._check_permissions(info.context.user)
        workflows = WorkflowService.get_workflows(**kwargs)
        if not workflows.get('success', False):
            raise ValueError(str(workflows))

        result = []
        for workflow in workflows['data']['workflows']:
            result.append(WorkflowGQLType(name=workflow.name, group=workflow.group))
        return result

    @staticmethod
    def _check_permissions(user):
        # The module's own right, and not individual's search right: the list of
        # workflows has nothing to do with the register of individuals, and that
        # borrowing tied their visibility to an unrelated entity. This helper existed
        # without ever being called - now it is.
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                WorkflowConfig.gql_workflow_search_perms):
            raise PermissionError("Unauthorized")
