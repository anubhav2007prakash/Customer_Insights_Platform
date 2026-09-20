"""Role hierarchy model to support inheritance."""
from __future__ import annotations

import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class RoleHierarchy(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "role_hierarchy"

    parent_role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)
    child_role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)

    # relationships are optional here; we keep simple foreign keys
