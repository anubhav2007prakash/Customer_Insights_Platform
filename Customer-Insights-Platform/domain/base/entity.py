"""Domain entity base class."""

from __future__ import annotations

import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DomainEntity(ABC):
    """
    Base domain entity — encapsulates business identity.

    Domain entities are independent of persistence (ORM) models.
    Mapping between ORM ↔ Domain happens in repositories.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DomainEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
