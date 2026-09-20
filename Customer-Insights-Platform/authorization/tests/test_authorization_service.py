"""Unit tests for AuthorizationService using mocked repository."""
from __future__ import annotations

import uuid
from authorization.services.authorization_service import AuthorizationService
from authorization.exceptions import PermissionDeniedException


class DummyRepo:
    def __init__(self):
        self._members = {}
        self._user_roles = {}
        self._roles = {}
        self._perms = {}
        self._role_perms = {}

    def get_user_org_membership(self, organization_id, user_id):
        return self._members.get((organization_id, user_id))

    def get_user_roles(self, organization_id, user_id):
        return self._user_roles.get((organization_id, user_id), [])

    def get_roles_permissions(self, role_ids):
        res = []
        for rid in role_ids:
            for pid in self._role_perms.get(rid, []):
                res.append(self._perms[pid])
        return res

    def get_role_by_id(self, role_id):
        return self._roles.get(role_id)

    def get_role_hierarchy_parents(self, role_id):
        return []

    def get_feature_flag(self, key: str):
        return None

    def get_org_feature_flag(self, organization_id, feature_flag_id):
        return None


class FakeRole:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class FakePermission:
    def __init__(self, id, code):
        self.id = id
        self.code = code


def test_has_permission_basic():
    repo = DummyRepo()
    svc = AuthorizationService(repo)
    org = uuid.uuid4()
    user = uuid.uuid4()
    role = uuid.uuid4()
    repo._members[(org, user)] = type("M", (), {"role_id": role})
    repo._roles[role] = FakeRole(role, "Organization Owner")
    perm = uuid.uuid4()
    repo._perms[perm] = FakePermission(perm, "customer.read")
    repo._role_perms[role] = [perm]

    assert svc.has_permission(user, org, "customer.read") is True
    assert svc.has_permission(user, org, "customer.delete") is False


def test_require_permission_raises():
    repo = DummyRepo()
    svc = AuthorizationService(repo)
    org = uuid.uuid4()
    user = uuid.uuid4()
    try:
        svc.require_permission(user, org, "analytics.read")
        raised = False
    except PermissionDeniedException:
        raised = True
    assert raised
