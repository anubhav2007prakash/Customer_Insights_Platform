"""Shared test fixtures for InsightForge AI backend."""

from __future__ import annotations

import uuid

import pytest

from core.config.environments import Environment
from core.config.settings import Settings
from core.di.container import reset_container
from core.types.common import TenantContext
from authentication.repositories.memory import MemoryAuthUnitOfWork
from bootstrap import bootstrap


@pytest.fixture(autouse=True)
def reset_di():
    """Reset DI container between tests."""
    yield
    reset_container()


@pytest.fixture(autouse=True)
def reset_memory_store():
    """Reset shared in-memory auth store between tests."""
    yield
    MemoryAuthUnitOfWork.reset_store()


@pytest.fixture
def test_settings() -> Settings:
    """Testing environment settings."""
    return Settings(
        environment=Environment.TESTING,
        debug=True,
        database__name="insightforge_test",
    )


@pytest.fixture
def tenant_context() -> TenantContext:
    """Sample tenant context for tests."""
    return TenantContext(
        organization_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        permissions=frozenset(["customers.read", "customers.write", "admin.full"]),
    )


@pytest.fixture
def app(test_settings: Settings):
    """Bootstrapped application."""
    bootstrap(test_settings)
    yield
    reset_container()
