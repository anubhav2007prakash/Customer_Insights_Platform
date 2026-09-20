"""Default IAM constants for InsightForge AI."""

OWNER_ROLE = "Owner"
MEMBER_ROLE = "Member"
DEFAULT_WORKSPACE_NAME = "Default Workspace"
DEFAULT_WORKSPACE_SLUG = "default"

DEFAULT_ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    OWNER_ROLE: (
        "admin.full",
        "users.read",
        "users.write",
        "roles.manage",
        "settings.manage",
        "reports.read",
        "reports.write",
    ),
    MEMBER_ROLE: (
        "customers.read",
        "analytics.read",
        "reports.read",
    ),
}

DEFAULT_NOTIFICATION_EVENTS: tuple[str, ...] = (
    "security.login",
    "security.password_changed",
    "security.email_verified",
    "product.welcome",
)

SECURITY_RELEVANT_EVENTS: tuple[str, ...] = (
    "registration",
    "login_success",
    "login_failure",
    "logout",
    "password_reset_requested",
    "password_reset_completed",
    "email_verification_requested",
    "email_verified",
    "account_locked",
    "account_unlocked",
)
