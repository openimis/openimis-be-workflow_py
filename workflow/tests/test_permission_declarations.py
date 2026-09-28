"""
Guard rails on workflow's rights declaration.

Same structure as `claim` and `core`: `DJANGO_PERMS` by entity then by action, and
`_PERM_CFG` deriving the config keys from it. The module is the smallest of the set -
one entity, one action, a single GraphQL entry point - but the failure modes are the
same, and silent:

  * `has_perms([])` returns True, so an empty list grants to everybody. That is the
    state `resolve_workflow` was in: no right required, not even authentication.
  * the identifier is what the roles carry (`RoleRight.right_id`): changing one
    withdraws access from every role that holds it.
  * a config key with no class attribute is never loaded by `_load_config` and reading
    it raises AttributeError - the right becomes unenforceable.

This module has **no django model at all** (`models.py` is empty, the workflows come
from `WorkflowService`), so there is no `get_rights` to test: the access point to the
configured value is `configured_perms`, checked here directly.
"""

from django.test import TestCase

from workflow.apps import (
    DJANGO_PERMS,
    WorkflowConfig,
    _PERM_CFG,
    configured_perms,
    django_perms,
    perms,
)

# The identifier as deployed. Changing one is incompatible with the existing roles:
# this test has to be updated *and* the new right granted.
EXPECTED_RIGHTS = {
    "gql_workflow_search_perms": ["210001"],
}


class WorkflowPermissionDeclarationTestCase(TestCase):
    def test_right_ids_unchanged(self):
        self.assertEqual(
            {key: getattr(WorkflowConfig, key) for key in EXPECTED_RIGHTS},
            EXPECTED_RIGHTS,
        )

    def test_perm_cfg_covers_every_declared_action(self):
        declared = {
            (entity, action)
            for entity, actions in DJANGO_PERMS.items()
            for action in actions
        }
        self.assertEqual(set(_PERM_CFG.values()), declared)

    def test_perm_cfg_matches_config_attributes(self):
        """`_load_config` ignores the keys with no class attribute."""
        missing = [key for key in _PERM_CFG if not hasattr(WorkflowConfig, key)]
        self.assertEqual(missing, [])

    def test_no_right_list_is_empty(self):
        empty = [key for key in _PERM_CFG if not getattr(WorkflowConfig, key)]
        self.assertEqual(empty, [])

    def test_attributes_carry_the_declared_right(self):
        """
        The rights are constants set from DJANGO_PERMS: the attribute must equal the
        declaration, without going through the config.
        """
        for key, (entity, action) in _PERM_CFG.items():
            with self.subTest(key=key):
                self.assertEqual(getattr(WorkflowConfig, key), perms(entity, action))

    def test_django_permission_names_are_unique(self):
        seen = {}
        for entity, actions in DJANGO_PERMS.items():
            for action, (name, _) in actions.items():
                seen.setdefault(name, []).append(f"{entity}.{action}")
        shared = {name: who for name, who in seen.items() if len(who) > 1}
        self.assertEqual(shared, {})

    def test_unknown_entity_or_action_raises(self):
        with self.assertRaises(KeyError):
            perms("nosuchentity", "query")
        with self.assertRaises(KeyError):
            perms("workflow", "nosuchaction")
        with self.assertRaises(KeyError):
            django_perms("workflow", "nosuchaction")

    # --- the access point to the configured value -------------------------
    # No `get_rights`: this module has no model, `configured_perms` is the only access
    # to the value `ModuleConfiguration` may have overridden.
    def test_configured_reads_the_value_not_the_declared_default(self):
        original = WorkflowConfig.gql_workflow_search_perms
        try:
            WorkflowConfig.gql_workflow_search_perms = ["999999"]
            self.assertEqual(configured_perms("workflow", "query"), ["999999"])
            self.assertEqual(perms("workflow", "query"), ["210001"])
        finally:
            WorkflowConfig.gql_workflow_search_perms = original

    def test_configured_returns_none_for_an_undeclared_action(self):
        """None means "no rule": the caller must fail closed."""
        self.assertIsNone(configured_perms("workflow", "nosuchaction"))

