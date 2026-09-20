"""Centralized normalization utilities (emails, phones, countries, etc.)."""
from __future__ import annotations

import re
from typing import Optional


def normalize_email(email: Optional[str]) -> Optional[str]:
    if not email:
        return None
    e = email.strip().lower()
    # simple Gmail alias strip
    if e.endswith("@gmail.com"):
        local, domain = e.split("@", 1)
        local = local.split("+")[0].replace(".", "")
        return f"{local}@{domain}"
    return e


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 7:
        return digits
    # naive E.164-ish normalization (no country code inference)
    if digits.startswith("0"):
        digits = digits.lstrip("0")
    return "+" + digits


def normalize_country(country: Optional[str]) -> Optional[str]:
    if not country:
        return None
    c = country.strip().lower()
    mapping = {"united states": "US", "usa": "US", "india": "IN", "uk": "GB"}
    return mapping.get(c, c.upper())
