from prowler.providers.kubernetes.services.rbac.lib.role_permissions import (
    check_role_permissions,
)
from prowler.providers.kubernetes.services.rbac.rbac_service import Rule


class TestCheckRolePermissions:
    def test_check_role_permissions(self):
        # Define some sample rules, resources, and verbs for testing
        rules = [
            # Rule 1: Allows 'get' and 'list' on 'pods' and 'services'
            Rule(resources=["pods", "services"], verbs=["get", "list"]),
            # Rule 2: Allows 'create' and 'delete' on 'deployments'
            Rule(resources=["deployments"], verbs=["create", "delete"]),
        ]
        resources = ["pods", "deployments"]
        verbs = ["get", "create"]

        assert check_role_permissions(rules, resources, verbs)

    def test_no_permissions(self):
        # Test when there are no rules
        rules = []
        resources = ["pods", "deployments"]
        verbs = ["get", "create"]

        assert not check_role_permissions(rules, resources, verbs)

    def test_no_matching_rules(self):
        # Test when there are rules, but none match the specified resources and verbs
        rules = [
            Rule(resources=["services"], verbs=["get", "list"]),
            Rule(resources=["pods"], verbs=["create", "delete"]),
        ]
        resources = ["deployments", "configmaps"]
        verbs = ["get", "create"]

        assert not check_role_permissions(rules, resources, verbs)

    def test_empty_rules(self):
        # Test when the rules list is empty
        rules = []
        resources = ["pods", "deployments"]
        verbs = ["get", "create"]

        assert not check_role_permissions(rules, resources, verbs)

    def test_empty_resources_and_verbs(self):
        # Test when resources and verbs are empty lists
        rules = [
            Rule(resources=["pods"], verbs=["get"]),
            Rule(resources=["services"], verbs=["list"]),
        ]
        resources = []
        verbs = []

        assert not check_role_permissions(rules, resources, verbs)

    def test_matching_rule_with_empty_resources_or_verbs(self):
        # Test when a rule matches, but either resources or verbs are empty
        rules = [
            Rule(resources=["pods"], verbs=["get"]),
            Rule(resources=["services"], verbs=["list"]),
        ]
        resources = []
        verbs = ["get"]

        assert not check_role_permissions(rules, resources, verbs)

        resources = ["pods"]
        verbs = []

        assert not check_role_permissions(rules, resources, verbs)
