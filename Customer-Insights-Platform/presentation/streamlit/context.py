"""Streamlit session context management."""

from __future__ import annotations

import uuid

import streamlit as st

from core.exceptions.base import TenantError
from core.types.common import TenantContext


def set_tenant_context(ctx: TenantContext) -> None:
    """Store tenant context in Streamlit session state."""
    st.session_state["_tenant_context"] = ctx


def get_tenant_context() -> TenantContext:
    """
    Retrieve tenant context from session.

    Raises:
        TenantError: When context is not initialized (user not authenticated).
    """
    ctx = st.session_state.get("_tenant_context")
    if ctx is None:
        org_id = st.session_state.get("if_org_id")
        user_id = st.session_state.get("if_user_id")
        if org_id and user_id:
            ctx = TenantContext(
                organization_id=uuid.UUID(str(org_id)) if not isinstance(org_id, uuid.UUID) else org_id,
                user_id=uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id,
                permissions=frozenset(st.session_state.get("if_permissions", [])),
            )
            set_tenant_context(ctx)
            return ctx
        raise TenantError(message="Authentication required.")
    return ctx
