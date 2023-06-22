import graphene

from core import ExtendedConnection


class WorkflowGQLType(graphene.ObjectType):
    name = graphene.String()
    group = graphene.String()

    class Meta:
        connection_class = ExtendedConnection
