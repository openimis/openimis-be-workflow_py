import graphene
from django.contrib.auth.models import AnonymousUser

from individual.apps import IndividualConfig

from workflow.gql_queries import WorkflowGQLType
from workflow.services import WorkflowService


class Query:
    workflow = graphene.Field(
        graphene.List(WorkflowGQLType),
        name=graphene.String(),
        group=graphene.String(),
    )

    def resolve_workflow(self, info, **kwargs):
        workflows = WorkflowService.get_workflows(**kwargs)
        if not workflows.get('success', False):
            raise ValueError(str(workflows))

        result = []
        for workflow in workflows['data']['workflows']:
            result.append(WorkflowGQLType(name=workflow.name, group=workflow.group))
        return result

    @staticmethod
    def _check_permissions(user):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                IndividualConfig.gql_individual_search_perms):
            raise PermissionError("Unauthorized")
