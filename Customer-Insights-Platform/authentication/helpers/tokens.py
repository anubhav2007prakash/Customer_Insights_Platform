"""Secure token generation and hashing."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPair:
    """Raw token and its persistence-safe hash."""

    raw: str
    token_hash: str


class TokenService:
    """Generate and verify opaque authentication tokens."""

    def __init__(self, secret_key: str) -> None:
        self._secret_key = secret_key.encode("utf-8")

    def generate(self, *, bytes_length: int = 32) -> TokenPair:
        raw = secrets.token_urlsafe(bytes_length)
        return TokenPair(raw=raw, token_hash=self.hash(raw))

    def hash(self, raw_token: str) -> str:
        digest = hmac.new(self._secret_key, raw_token.encode("utf-8"), hashlib.sha256).hexdigest()
        return digest

    def verify(self, raw_token: str, token_hash: str) -> bool:
        return hmac.compare_digest(self.hash(raw_token), token_hash)
