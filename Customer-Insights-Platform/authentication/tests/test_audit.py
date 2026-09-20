"""Unit tests for auth audit logging."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from database.enums import AuditAction
from authentication.audit import AuthAuditLogger
from authentication.repositories.memory import MemoryAuditRepository, MemoryAuthStore


class TestAuthAuditLogger:
    """Audit logger tests."""

    def test_audit_creates_log_entry(self) -> None:
        store = MemoryAuthStore()
        repo = MemoryAuditRepository(store)
        logger = AuthAuditLogger(repo)
        user_id = uuid.uuid4()
        org_id = uuid.uuid4()

        log = logger.audit(
            action=AuditAction.LOGIN,
            entity_type="session",
            organization_id=org_id,
            user_id=user_id,
            entity_id=user_id,
            ip_address="127.0.0.1",
            user_agent="test-agent",
        )
        assert log.action == AuditAction.LOGIN
        assert log.entity_type == "session"
        assert log.user_id == user_id
        assert log.organization_id == org_id
        assert len(store.audit_logs) == 1

    def test_audit_with_old_and_new_values(self) -> None:
        store = MemoryAuthStore()
        repo = MemoryAuditRepository(store)
        logger = AuthAuditLogger(repo)

        log = logger.audit(
            action=AuditAction.UPDATE,
            entity_type="user",
            old_values={"status": "pending"},
            new_values={"status": "active"},
        )
        assert log.old_values == {"status": "pending"}
        assert log.new_values == {"status": "active"}

    def test_security_event_creates_event(self) -> None:
        store = MemoryAuthStore()
        repo = MemoryAuditRepository(store)
        logger = AuthAuditLogger(repo)

        event = logger.security_event(
            event_type="login_failure",
            description="Failed login attempt",
            severity="warning",
            metadata={"attempts": 3},
        )
        assert event.event_type == "login_failure"
        assert event.severity == "warning"
        assert len(store.security_events) == 1

    def test_login_history_records_success(self) -> None:
        store = MemoryAuthStore()
        repo = MemoryAuditRepository(store)
        logger = AuthAuditLogger(repo)
        user_id = uuid.uuid4()

        hist = logger.login_history(
            user_id=user_id,
            organization_id=None,
            success=True,
            ip_address="10.0.0.1",
            user_agent="chrome",
        )
        assert hist.success is True
        assert hist.ip_address == "10.0.0.1"
        assert len(store.login_history) == 1

    def test_login_history_records_failure_with_reason(self) -> None:
        store = MemoryAuthStore()
        repo = MemoryAuditRepository(store)
        logger = AuthAuditLogger(repo)
        user_id = uuid.uuid4()

        hist = logger.login_history(
            user_id=user_id,
            organization_id=None,
            success=False,
            failure_reason="invalid_password",
        )
        assert hist.success is False
        assert hist.failure_reason == "invalid_password"
