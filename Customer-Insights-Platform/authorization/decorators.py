"""Decorators for permission and feature checks usable in Streamlit pages."""
from __future__ import annotations

from functools import wraps
from typing import Callable

from authorization.context import get_current_user, get_current_organization_id
from authorization.services.authorization_service import AuthorizationService
from authorization.exceptions import PermissionDeniedException, FeatureDisabledException


def require_permission(permission: str):
    def _decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            org = get_current_organization_id()
            if not user or not org:
                raise PermissionDeniedException("Unauthenticated or missing organization context")
            svc = AuthorizationService()
            if not svc.has_permission(user.id, org, permission):
                raise PermissionDeniedException(f"Permission denied: {permission}")
            return fn(*args, **kwargs)

        return wrapper

    return _decorator


def require_role(role_name: str):
    def _decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            org = get_current_organization_id()
            if not user or not org:
                raise PermissionDeniedException("Unauthenticated or missing organization context")
            svc = AuthorizationService()
            if not svc.has_role(user.id, org, role_name):
                raise PermissionDeniedException(f"Role required: {role_name}")
            return fn(*args, **kwargs)

        return wrapper

    return _decorator


def require_feature(feature_key: str):
    def _decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            org = get_current_organization_id()
            if not org:
                raise FeatureDisabledException("Missing organization context for feature check")
            svc = AuthorizationService()
            if not svc.is_feature_enabled(org, feature_key):
                raise FeatureDisabledException(f"Feature disabled: {feature_key}")
            return fn(*args, **kwargs)

        return wrapper

    return _decorator


def organization_required(fn: Callable):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        org = get_current_organization_id()
        if not org:
            raise PermissionDeniedException("Organization context required")
        return fn(*args, **kwargs)

    return wrapper
