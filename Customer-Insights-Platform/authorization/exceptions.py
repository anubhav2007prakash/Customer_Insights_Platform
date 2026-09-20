"""Authorization-related exceptions."""

class AuthorizationError(Exception):
    pass


class PermissionDeniedException(AuthorizationError):
    pass


class RoleNotFoundException(AuthorizationError):
    pass


class InvalidPermissionException(AuthorizationError):
    pass


class FeatureDisabledException(AuthorizationError):
    pass


class SubscriptionRequiredException(AuthorizationError):
    pass


class TenantIsolationException(AuthorizationError):
    pass


class OwnershipViolationException(AuthorizationError):
    pass
