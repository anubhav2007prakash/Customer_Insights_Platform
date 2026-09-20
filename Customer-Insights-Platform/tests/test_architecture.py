"""Architecture validation tests."""

from __future__ import annotations

import uuid

import pytest

from core.di.container import get_container
from core.events.base import CustomerCreated
from core.interfaces.event_bus import EventBusPort
from core.exceptions.base import ValidationError
from core.security.password import PasswordHasher
from core.types.common import PaginationParams, TenantContext
from core.validation.base import validate_request
from pydantic import BaseModel, Field


class SampleRequest(BaseModel):
    name: str = Field(min_length=1)


def test_di_container_resolves_defaults(app):
    container = get_container()
    bus = container.resolve(EventBusPort)
    assert bus is not None


def test_event_bus_publish(app):
    received = []
    bus = get_container().resolve(EventBusPort)
    bus.subscribe(CustomerCreated, lambda e: received.append(e))
    bus.publish(CustomerCreated(customer_id=uuid.uuid4()))
    assert len(received) == 1


def test_password_hasher(app):
    hasher = PasswordHasher()
    hashed = hasher.hash("securepassword123")
    assert hasher.verify("securepassword123", hashed)
    assert not hasher.verify("wrong", hashed)


def test_validation_raises_on_invalid():
    with pytest.raises(ValidationError):
        validate_request(SampleRequest, {"name": ""})


def test_pagination_params():
    p = PaginationParams(page=2, page_size=25)
    assert p.offset == 25
    assert p.limit == 25


def test_tenant_context_permissions(tenant_context):
    assert "customers.read" in tenant_context.permissions
