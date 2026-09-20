"""Policy evaluator implementing ABAC and PBAC via expression evaluation."""
from __future__ import annotations

from typing import Any, Dict, Tuple
from authorization.policies.expressions import evaluate_expression
from authorization.repositories.sqlalchemy import AuthorizationRepository


class PolicyEvaluator:
    def __init__(self, repo: AuthorizationRepository | None = None):
        self.repo = repo or AuthorizationRepository()

    def evaluate(self, user, organization_id, action: str, resource: Any, context: Dict) -> Tuple[bool, str]:
        """Return (allowed, reason).

        Simple rules implemented here:
        - If user has role with permission {resource}.{action} -> allow
        - If policy expressions exist in DB, evaluate them
        - If resource.owner_id == user.id and action in owner-scoped perms -> allow
        - Else deny
        """
        # check explicit role permissions via AuthorizationService repository
        role_ids = []
        membership = self.repo.get_user_org_membership(organization_id, user.id)
        if membership and membership.role_id:
            role_ids.append(membership.role_id)
        user_roles = self.repo.get_user_roles(organization_id, user.id)
        for ur in user_roles:
            role_ids.append(ur.role_id)

        perms = self.repo.get_roles_permissions(role_ids)
        target = f"{resource.__class__.__name__.lower()}.{action}" if hasattr(resource, "__class__") else action
        perm_codes = {p.code for p in perms}
        if target in perm_codes or action in perm_codes:
            return True, "role_permission"

        # ownership
        if hasattr(resource, "owner_id") and getattr(resource, "owner_id") == user.id:
            owner_perm = f"{resource.__class__.__name__.lower()}.{action}.own"
            if owner_perm in perm_codes:
                return True, "owner_permission"

        # policy expressions (placeholder: repo could return matching policy rules)
        # For now support simple expression in context: context.get("policy_expression")
        expr = context.get("policy_expression")
        if expr:
            ok = evaluate_expression(expr, user=user, resource=resource, context=context)
            return (True, "expression") if ok else (False, "expression_false")

        return False, "no_match"
