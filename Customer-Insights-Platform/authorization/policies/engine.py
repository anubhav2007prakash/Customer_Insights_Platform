"""Central Policy Engine implementing evaluation and RLS helpers."""
from __future__ import annotations

from typing import Any, Dict, Optional
from authorization.policies.evaluator import PolicyEvaluator
from authorization.policies.expressions import evaluate_expression
from authorization.repositories.sqlalchemy import AuthorizationRepository
from authorization.context import get_current_user, get_current_organization_id
from authorization.policies.models import PolicyAuditLog
from database.session import SessionLocal
from sqlalchemy import and_


class PolicyEngine:
    """Evaluate policies, perform ABAC checks, and provide RLS helper.

    This engine is designed to be modular: concrete policy storage and evaluators
    can be plugged in.
    """

    def __init__(self, repo: AuthorizationRepository | None = None):
        self.repo = repo or AuthorizationRepository()
        self.evaluator = PolicyEvaluator(self.repo)

    def evaluate(self, action: str, resource: dict | Any, context: Optional[Dict[str, Any]] = None) -> bool:
        user = get_current_user()
        org = get_current_organization_id()
        if user is None or org is None:
            self._audit(user, org, action, resource, False, "missing_context")
            return False

        # Let evaluator do the heavy lifting
        allowed, reason = self.evaluator.evaluate(user, org, action, resource, context or {})
        self._audit(user, org, action, resource, allowed, reason)
        return allowed

    def can_read(self, resource: dict | Any, context: Optional[Dict[str, Any]] = None) -> bool:
        return self.evaluate("read", resource, context)

    def can_update(self, resource: dict | Any, context: Optional[Dict[str, Any]] = None) -> bool:
        return self.evaluate("update", resource, context)

    def can_export(self, resource: dict | Any, context: Optional[Dict[str, Any]] = None) -> bool:
        return self.evaluate("export", resource, context)

    def rls_filter(self, model, user=None, organization_id=None):
        """Return a SQLAlchemy filter expression to apply for row-level security.

        Callers should combine this with their select statements. This simple
        implementation enforces organization isolation and supports ownership and
        team/department scope by inspecting common column names.
        """
        user = user or get_current_user()
        organization_id = organization_id or get_current_organization_id()
        clauses = []
        if hasattr(model.c, "organization_id"):
            clauses.append(model.c.organization_id == organization_id)

        # Owner access: allow rows where owner_id == user.id
        if hasattr(model.c, "owner_id") and user is not None:
            clauses.append(model.c.owner_id == user.id)

        # Team/department access is implementation-specific; leave hook for repo
        # The default is organization-limited + owner matches
        if clauses:
            return and_(*clauses)
        return None

    def _audit(self, user, org, action, resource, allowed: bool, reason: str | None = None) -> None:
        try:
            db = SessionLocal()
            entry = PolicyAuditLog(
                user_id=getattr(user, "id", None),
                organization_id=org,
                action=action,
                resource=str(getattr(resource, "id", None) or resource),
                allowed=allowed,
                reason=reason or "",
            )
            db.add(entry)
            db.flush()
            db.commit()
        except Exception:
            # Fail open for audit failures (do not block authorization)
            try:
                db.rollback()
            except Exception:
                pass
        finally:
            try:
                db.close()
            except Exception:
                pass
