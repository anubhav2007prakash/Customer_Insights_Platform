"""Validation framework built on Pydantic v2."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError as PydanticValidationError

from core.exceptions.base import ValidationError

T = TypeVar("T", bound=BaseModel)


def validate_request(schema: type[T], data: dict[str, Any] | BaseModel) -> T:
    """
    Validate incoming data against a Pydantic schema.

    Raises:
        ValidationError: When validation fails with field-level details.
    """
    try:
        if isinstance(data, schema):
            return data
        return schema.model_validate(data)
    except PydanticValidationError as exc:
        raise ValidationError(
            message="Request validation failed.",
            details={"errors": exc.errors()},
        ) from exc


class RequestSchema(BaseModel):
    """Base class for all inbound request DTOs."""

    model_config = {"str_strip_whitespace": True, "extra": "forbid"}


class ResponseSchema(BaseModel):
    """Base class for all outbound response DTOs."""

    model_config = {"from_attributes": True}
