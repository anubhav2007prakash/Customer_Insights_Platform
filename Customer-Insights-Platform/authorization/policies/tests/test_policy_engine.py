"""Basic tests for policy engine and expression evaluator."""
from __future__ import annotations

import uuid
from authorization.policies.engine import PolicyEngine
from authorization.policies.expressions import evaluate_expression


class DummyUser:
    def __init__(self, id, department=None, team=None):
        self.id = id
        self.department = department
        self.team = team


class DummyResource:
    def __init__(self, id, department=None, owner_id=None):
        self.id = id
        self.department = department
        self.owner_id = owner_id


def test_expression_eval_basic():
    user = DummyUser(id=1, department="marketing")
    res = DummyResource(id=2, department="marketing")
    expr = "User.department == Resource.department"
    assert evaluate_expression(expr, user=user, resource=res, context={}) is True


def test_policy_engine_denies_without_context():
    engine = PolicyEngine()
    res = DummyResource(id=2, department="marketing")
    assert engine.evaluate("read", res, context={}) is False
