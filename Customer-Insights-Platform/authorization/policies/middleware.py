"""Middleware helpers to inject RLS filters into repository queries."""
from __future__ import annotations

from sqlalchemy.sql import Select
from authorization.policies.engine import PolicyEngine


def apply_rls_to_select(stmt: Select, model, user=None, organization_id=None) -> Select:
    engine = PolicyEngine()
    filt = engine.rls_filter(model, user=user, organization_id=organization_id)
    if filt is not None:
        return stmt.where(filt)
    return stmt
