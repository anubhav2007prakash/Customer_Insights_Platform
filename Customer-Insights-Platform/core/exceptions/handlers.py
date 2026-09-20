"""Exception handling utilities for presentation and logging layers."""

from __future__ import annotations

import logging
from typing import Any

from core.exceptions.base import InsightForgeError

logger = logging.getLogger("insightforge.errors")


def to_user_message(error: Exception) -> str:
    """Return a safe, user-facing message without leaking internals."""
    if isinstance(error, InsightForgeError):
        return error.message
    return "An unexpected error occurred. Please try again or contact support."


def handle_exception(error: Exception, *, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Log technical details and return a safe response payload.

    Args:
        error: The caught exception.
        context: Optional context (user_id, org_id, action).

    Returns:
        Dict suitable for presentation layer display.
    """
    ctx = context or {}
    if isinstance(error, InsightForgeError):
        log_level = logging.WARNING if error.code.startswith("VALIDATION") else logging.ERROR
        logger.log(
            log_level,
            "[%s] %s | details=%s context=%s",
            error.code,
            error.message,
            error.details,
            ctx,
            exc_info=error.cause,
        )
        return error.to_dict()

    logger.exception("Unhandled exception | context=%s", ctx)
    return {
        "code": "INTERNAL_ERROR",
        "message": to_user_message(error),
        "details": {},
    }
