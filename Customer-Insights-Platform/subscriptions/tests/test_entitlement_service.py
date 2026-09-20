"""Unit tests for EntitlementService."""
from __future__ import annotations

import uuid
from subscriptions.services.entitlement_service import EntitlementService


class DummyRepo:
    def __init__(self):
        self.features = {}
        self.entitlements = {}
        self.modules = {}

    def get_feature_by_key(self, key: str):
        return self.features.get(key)

    def get_entitlement(self, organization_id, feature_id):
        return self.entitlements.get((organization_id, feature_id))

    def get_module_license(self, organization_id, module_key):
        return self.modules.get((organization_id, module_key))


class FakeFeature:
    def __init__(self, id, key, default_enabled=False):
        self.id = id
        self.key = key
        self.default_enabled = default_enabled


class FakeEntitlement:
    def __init__(self, id, enabled):
        self.id = id
        self.enabled = enabled


class FakeModule:
    def __init__(self, id, enabled):
        self.id = id
        self.enabled = enabled


def test_has_feature_default_disabled():
    repo = DummyRepo()
    feat_id = uuid.uuid4()
    repo.features["ai_chat"] = FakeFeature(feat_id, "ai_chat", default_enabled=False)
    svc = EntitlementService(repo)
    org = uuid.uuid4()
    assert svc.has_feature(org, "ai_chat") is False


def test_has_feature_entitled():
    repo = DummyRepo()
    feat_id = uuid.uuid4()
    repo.features["ai_chat"] = FakeFeature(feat_id, "ai_chat", default_enabled=False)
    repo.entitlements[(1, feat_id)] = FakeEntitlement(feat_id, True)
    svc = EntitlementService(repo)
    assert svc.has_feature(1, "ai_chat") is True


def test_can_use_ai_module():
    repo = DummyRepo()
    repo.modules[(1, "ai_pack")] = FakeModule(1, True)
    svc = EntitlementService(repo)
    assert svc.can_use_ai(1) is True
