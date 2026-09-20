"""Decorators to enforce policy checks and masking on functions/endpoints."""
from __future__ import annotations

from functools import wraps
from typing import Callable

from authorization.policies.engine import PolicyEngine
from authorization.context import get_current_user, get_current_organization_id
from authorization.exceptions import PermissionDeniedException


def require_policy(action: str, resource_resolver: Callable[..., object] | None = None):
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            org = get_current_organization_id()
            engine = PolicyEngine()
            resource = resource_resolver(*args, **kwargs) if resource_resolver else kwargs.get("resource")
            if not engine.evaluate(action, resource, context={}) :
                raise PermissionDeniedException(f"Policy denied for action {action}")
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def mask_fields(mask_map: dict):
    """Decorator to mask specified fields according to mask_map: {field: strategy}.

    Example:
        @mask_fields({"email":"email","phone":"phone"})
        def get_user(...):
            return user_dict
    """
    from authorization.policies.masking import apply_mask

    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            if not isinstance(result, dict):
                return result
            for f, strat in mask_map.items():
                if f in result and result[f]:
                    result[f] = apply_mask(result[f], strat)
            return result

        return wrapper

    return decorator
