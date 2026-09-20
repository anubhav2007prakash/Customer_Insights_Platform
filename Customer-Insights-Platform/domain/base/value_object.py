"""Value object base class."""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject(ABC):
    """
    Immutable value object base.

    Value objects have no identity — equality is by value.
    """
