"""External provider abstractions for auth workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class EmailProvider(Protocol):
    """Email sender port."""

    def send_verification_email(self, *, email: str, token: str, full_name: str) -> None:
        ...

    def send_password_reset_email(self, *, email: str, token: str, full_name: str | None = None) -> None:
        ...

    def send_password_changed_email(self, *, email: str, full_name: str | None = None) -> None:
        ...


@dataclass
class SentEmail:
    """Captured email for tests and local development."""

    kind: str
    email: str
    token: str | None = None
    full_name: str | None = None


@dataclass
class MockEmailProvider:
    """Mock provider that records messages without external I/O."""

    sent: list[SentEmail] = field(default_factory=list)

    def send_verification_email(self, *, email: str, token: str, full_name: str) -> None:
        self.sent.append(SentEmail(kind="verification", email=email, token=token, full_name=full_name))

    def send_password_reset_email(self, *, email: str, token: str, full_name: str | None = None) -> None:
        self.sent.append(SentEmail(kind="password_reset", email=email, token=token, full_name=full_name))

    def send_password_changed_email(self, *, email: str, full_name: str | None = None) -> None:
        self.sent.append(SentEmail(kind="password_changed", email=email, full_name=full_name))
