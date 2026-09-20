"""Payment provider abstraction for InsightForge AI."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PaymentProvider(ABC):
    """Abstract payment provider interface."""

    @abstractmethod
    def create_customer(self, payload: Any) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def create_order(self, payload: Any) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def create_subscription(self, payload: Any) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def capture_payment(self, payment_id: str, amount: int | None = None) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def verify_signature(self, signature: str, payload: bytes, secret: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def pause_subscription(self, subscription_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def resume_subscription(self, subscription_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def create_refund(
        self,
        payment_id: str,
        amount: int | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_payment_status(self, payment_id: str) -> dict[str, Any]:
        raise NotImplementedError
