"""Razorpay client wrapper for InsightForge AI."""
from __future__ import annotations

import importlib
import os

from billing.razorpay.exceptions import RazorpayConnectionError


class RazorpayClient:
    def __init__(self, api_key: str | None = None, api_secret: str | None = None):
        self.api_key = api_key or os.getenv("RAZORPAY_API_KEY")
        self.api_secret = api_secret or os.getenv("RAZORPAY_API_SECRET")
        if not self.api_key or not self.api_secret:
            raise RazorpayConnectionError("Razorpay API credentials are not configured")

        try:
            razorpay = importlib.import_module("razorpay")
        except ModuleNotFoundError as exc:
            raise RazorpayConnectionError("Razorpay SDK is not installed") from exc

        self.client = razorpay.Client(auth=(self.api_key, self.api_secret))

    def create_customer(self, name: str | None, email: str, contact: str | None = None, company_name: str | None = None, metadata: dict | None = None) -> dict:
        payload = {
            "name": name,
            "email": email,
            "contact": contact,
            "type": "company" if company_name else "individual",
            "notes": {"company_name": company_name} if company_name else {},
        }
        return self.client.customer.create({k: v for k, v in payload.items() if v is not None})

    def create_order(self, amount: int, currency: str, receipt: str, notes: dict | None = None) -> dict:
        return self.client.order.create({
            "amount": amount,
            "currency": currency,
            "receipt": receipt,
            "payment_capture": 1,
            "notes": notes or {},
        })

    def create_subscription(self, customer_id: str, plan_id: str, total_count: int | None = None, trial_days: int | None = None, start_at: int | None = None, notes: dict | None = None) -> dict:
        payload = {
            "plan_id": plan_id,
            "customer_notify": 1,
            "customer_id": customer_id,
            "total_count": total_count,
            "start_at": start_at,
            "trial_end": trial_days and (int(__import__("time").time()) + trial_days * 86400),
            "notes": notes or {},
        }
        return self.client.subscription.create({k: v for k, v in payload.items() if v is not None})

    def capture_payment(self, payment_id: str, amount: int | None = None) -> dict:
        payload = {"amount": amount} if amount else {}
        return self.client.payment.capture(payment_id, payload)

    def verify_signature(self, signature: str, payload: bytes, secret: str) -> dict:
        try:
            return self.client.utility.verify_payment_signature({
                "razorpay_signature": signature,
                "razorpay_payload": payload.decode("utf-8"),
            })
        except Exception as exc:
            raise RazorpayConnectionError("Razorpay signature verification failed") from exc

    def cancel_subscription(self, subscription_id: str) -> dict:
        return self.client.subscription.cancel(subscription_id)

    def pause_subscription(self, subscription_id: str) -> dict:
        return self.client.subscription.update(subscription_id, {"paused": True})

    def resume_subscription(self, subscription_id: str) -> dict:
        return self.client.subscription.update(subscription_id, {"paused": False})

    def create_refund(self, payment_id: str, amount: int | None = None, notes: dict | None = None) -> dict:
        payload = {"payment_id": payment_id, "amount": amount} if amount else {"payment_id": payment_id}
        if notes:
            payload["notes"] = notes
        return self.client.payment.refund(payload)

    def get_payment(self, payment_id: str) -> dict:
        return self.client.payment.fetch(payment_id)
