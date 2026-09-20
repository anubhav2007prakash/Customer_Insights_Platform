"""Lightweight request/user context used by decorators and services."""
from __future__ import annotations

import threading
from typing import Optional

_thread_locals = threading.local()


def set_current_user(user, organization_id=None):
    _thread_locals.current_user = user
    _thread_locals.organization_id = organization_id


def get_current_user():
    return getattr(_thread_locals, "current_user", None)


def get_current_organization_id():
    return getattr(_thread_locals, "organization_id", None)


def clear():
    if hasattr(_thread_locals, "current_user"):
        del _thread_locals.current_user
    if hasattr(_thread_locals, "organization_id"):
        del _thread_locals.organization_id
