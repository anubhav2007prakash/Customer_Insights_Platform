"""Field-level masking utilities."""
from __future__ import annotations

import re
from typing import Optional


def mask_email(email: str) -> str:
    try:
        local, domain = email.split("@", 1)
        if len(local) <= 2:
            local_mask = local[0] + "*"
        else:
            local_mask = local[:2] + "*" * (len(local) - 2)
        return f"{local_mask}@{domain}"
    except Exception:
        return "***"


def mask_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if len(digits) <= 4:
        return "*" * len(digits)
    return "*" * (len(digits) - 4) + digits[-4:]


def mask_credit_card(cc: str) -> str:
    digits = re.sub(r"\D", "", cc)
    if len(digits) <= 4:
        return "*" * len(digits)
    return "*" * (len(digits) - 4) + digits[-4:]


def apply_mask(value: str, strategy: str, params: Optional[dict] = None) -> str:
    if value is None:
        return value
    if strategy == "email":
        return mask_email(value)
    if strategy == "phone":
        return mask_phone(value)
    if strategy == "credit_card":
        return mask_credit_card(value)
    if strategy == "first_letter":
        return value[0] + "*" * (len(value) - 1)
    if strategy == "hidden":
        return "[REDACTED]"
    return "[REDACTED]"
