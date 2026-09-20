"""Domain event base classes."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class EventMetadata:
    """Context attached to every domain event."""

    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    organization_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    correlation_id: str | None = None


@dataclass(frozen=True)
class DomainEvent:
    """
    Base class for all internal domain events.

    Subclass and define event-specific payload fields.
    """

    metadata: EventMetadata = field(default_factory=EventMetadata)

    @property
    def event_name(self) -> str:
        return self.__class__.__name__

    def to_dict(self) -> dict[str, Any]:
        """Serialize event for logging or message queues."""
        return {
            "event": self.event_name,
            "event_id": str(self.metadata.event_id),
            "occurred_at": self.metadata.occurred_at.isoformat(),
            "organization_id": str(self.metadata.organization_id) if self.metadata.organization_id else None,
            "payload": {
                k: v for k, v in self.__dict__.items() if k != "metadata"
            },
        }


# ── Canonical event stubs (handlers registered by modules later) ──────────────

@dataclass(frozen=True)
class CustomerCreated(DomainEvent):
    customer_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class CampaignCompleted(DomainEvent):
    campaign_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class PredictionGenerated(DomainEvent):
    prediction_id: uuid.UUID = field(default_factory=uuid.uuid4)
    model_version: str = ""


@dataclass(frozen=True)
class ReportExported(DomainEvent):
    report_id: uuid.UUID = field(default_factory=uuid.uuid4)
    format: str = "pdf"


@dataclass(frozen=True)
class InvoicePaid(DomainEvent):
    invoice_id: uuid.UUID = field(default_factory=uuid.uuid4)
    amount: float = 0.0


@dataclass(frozen=True)
class AIInsightGenerated(DomainEvent):
    insight_id: uuid.UUID = field(default_factory=uuid.uuid4)
    severity: str = "info"
