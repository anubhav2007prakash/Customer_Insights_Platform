from __future__ import annotations


class DataQualityError(Exception):
    pass


class SchemaValidationError(DataQualityError):
    pass


class DriftDetectionError(DataQualityError):
    pass
