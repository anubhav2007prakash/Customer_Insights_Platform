"""Centralized authentication audit logging."""

from __future__ import annotations

import uuid
from typing import Any

from core.logging.logger import get_logger
from database.enums import AuditAction
from database.models.auth import LoginHistory
from database.models.security import AuditLog, SecurityEvent
from authentication.repositories.interfaces import AuditRepository

logger = get_logger("authentication.audit")


class AuthAuditLogger:
    """Writes auth events to both Python logs and audit tables."""

    def __init__(self, repository: AuditRepository) -> None:
        self.repository = repository

    def audit(
        self,
        *,
        action: AuditAction,
        entity_type: str,
        organization_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        entity_id: uuid.UUID | None = None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        logger.info("auth_audit action=%s user_id=%s org_id=%s", action.value, user_id, organization_id)
        return self.repository.add_audit(
            AuditLog(
                organization_id=organization_id,
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )

    def security_event(
        self,
        *,
        event_type: str,
        description: str,
        severity: str = "info",
        organization_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityEvent:
        logger.warning("auth_security_event type=%s severity=%s user_id=%s", event_type, severity, user_id)
        return self.repository.add_security_event(
            SecurityEvent(
                organization_id=organization_id,
                user_id=user_id,
                event_type=event_type,
                severity=severity,
                description=description,
                ip_address=ip_address,
                metadata_=metadata or {},
            )
        )

    def login_history(
        self,
        *,
        user_id: uuid.UUID,
        organization_id: uuid.UUID | None,
        success: bool,
        ip_address: str | None = None,
        user_agent: str | None = None,
        failure_reason: str | None = None,
    ) -> LoginHistory:
        return self.repository.add_login_history(
            LoginHistory(
                user_id=user_id,
                organization_id=organization_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                failure_reason=failure_reason,
            )
        )
