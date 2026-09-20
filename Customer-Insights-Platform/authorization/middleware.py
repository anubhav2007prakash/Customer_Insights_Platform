"""Middleware helpers to enforce tenant isolation and set context.

These are lightweight utilities because the platform may be used with Streamlit.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from authorization.context import set_current_user, clear
from database.session import SessionLocal
from database.models.tenant import Organization


@contextmanager
def tenant_scope(user, organization_id):
    """Set the thread-local context for the duration of a block.

    Example:
        with tenant_scope(current_user, org_id):
            # downstream code sees current user/org
    """
    try:
        set_current_user(user, organization_id)
        yield
    finally:
        clear()


def enforce_tenant_on_query(session, organization_id):
    """Helper to apply tenant filter on ORM queries if desired.

    This is a noop here; call from repository-level queries where applicable.
    """
    return session
