# InsightForge AI - Authentication & Identity Management

## Architecture

The authentication module follows **Clean Architecture**, **SOLID principles**, and **Domain-Driven Design** patterns.

```
authentication/
├── models/              - ORM entity extensions (if any)
├── schemas/             - Pydantic request/response schemas (auth.py)
├── services/            - Application service layer (business logic)
│   ├── registration.py  - Organization and user registration workflows
│   ├── login.py         - Authentication, lockout, session creation
│   ├── sessions.py      - Session validation and revocation
│   ├── password_reset.py - Password reset and change workflows
│   ├── email_verification.py - Email verification workflows
│   ├── profile.py       - User profile building utilities
│   ├── providers.py     - Email provider abstractions
│   └── factory.py       - Dependency injection composition
├── repositories/        - Data persistence layer (ports/adapters)
│   ├── interfaces.py    - Abstract repository protocols
│   ├── sqlalchemy.py    - SQLAlchemy implementation
│   └── memory.py        - In-memory implementation for tests
├── validators/          - Input and policy validators
│   ├── password_policy.py - Configurable password rules
│   └── inputs.py        - Username, phone, organization validation
├── middleware/          - Framework integration helpers
│   └── session_context.py - Token validation middleware
├── decorators/          - Presentation layer access control
│   └── access.py        - Streamlit/Python decorators
├── permissions/         - RBAC primitives
│   └── rbac.py          - Permission checking service
├── policies/            - Zero-trust authorization policies
│   └── account_policy.py - Account/organization status checks
├── events/              - Domain events
│   └── auth_events.py   - Authentication domain events
├── audit/               - Audit logging
│   └── logger.py        - Centralized audit logger
├── exceptions/          - Custom exception hierarchy
│   └── __init__.py
├── helpers/             - Utility functions
│   ├── password_hasher.py - Passlib bcrypt wrapper
│   ├── tokens.py         - Secure token generation
│   ├── normalization.py  - Email/username normalization
│   └── time.py           - UTC timestamp helper
└── constants/           - Default values and configuration
    └── defaults.py
```

## Registration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 RegisterOrganizationRequest                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Validate password policy (PasswordPolicyValidator)      │
│  2. Normalize email and username                           │
│  3. Check for duplicate email/username/organization       │
│  4. Begin transaction (AuthUnitOfWork)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Create Organization (trial status)                     │
│  6. Create default Workspace                               │
│  7. Create Owner Role                                      │
│  8. Create User (pending verification)                     │
│  9. Build UserProfile (split full name, calculate %)       │
│ 10. Initialize UserPreference and NotificationSettings      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 11. Create OrganizationMember (is_owner=True)               │
│ 12. Assign UserRole                                       │
│ 13. Record PasswordHistory                                 │
│ 14. Generate email verification token                       │
│ 15. Send verification email (via EmailProvider)             │
│ 16. Create welcome notification                            │
│ 17. Write audit log (AuditAction.CREATE)                   │
│ 18. Publish UserRegistered event                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Return RegistrationResponse                     │
└─────────────────────────────────────────────────────────────┘
```

**Transactional guarantee**: All database operations occur within a single transaction. On any failure, all changes are rolled back.

## Login Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      LoginRequest                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Find user by email or username (identifier)             │
│  2. Validate password using bcrypt                           │
│  3. Check organization status (if specified)                 │
│  4. Verify user is organization member (if specified)       │
│  5. Apply AccountPolicy checks:                            │
│     - Account not locked                                    │
│     - Account not deleted/suspended                         │
│     - Email verified (if required)                          │
│     - Password not expired                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Reset failed_login_attempts                            │
│  7. Clear locked_until                                     │
│  8. Update last_login_at                                   │
│  9. Generate session token (TokenService)                    │
│ 10. Create UserSession (with device info)                  │
│ 11. Write login history and audit log                       │
│ 12. Publish LoginSucceeded event                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Return LoginResponse                          │
└─────────────────────────────────────────────────────────────┘

On failure: Increment failed_login_attempts, lock if threshold exceeded,
record failure, publish LoginFailed, create SecurityEvent.
```

## Password Lifecycle

### Password Policy

Configurable via `SecuritySettings`:

| Setting | Default | Description |
|---------|---------|-------------|
| `password_min_length` | 8 | Minimum password length |
| `password_max_length` | 128 | Maximum password length |
| `password_require_uppercase` | true | Require A-Z |
| `password_require_lowercase` | true | Require a-z |
| `password_require_numeric` | true | Require 0-9 |
| `password_require_special` | true | Require non-alphanumeric |
| `password_history_count` | 5 | Prevent reuse |
| `password_expiration_days` | 90 | Expiry duration |

### Password Reset Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  ForgotPasswordRequest                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Find user by email (never reveal existence)             │
│  2. Generate one-time reset token                            │
│  3. Store PasswordResetToken with expiry                     │
│  4. Log audit event                                          │
│  5. Send email (if user exists)                             │
│  6. Return generic response (always accepted=True)            │
└─────────────────────────────────────────────────────────────┘

User clicks link with token:
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              PasswordResetRequest with token                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Validate password policy                                 │
│  2. Find valid unused reset token                            │
│  3. Check password not in history                            │
│  4. Hash new password                                        │
│  5. Update user.password_hash                                │
│  6. Update password_changed_at, password_expires_at            │
│  7. Record PasswordHistory                                   │
│  8. Mark token used                                          │
│  9. Revoke all existing sessions                               │
│ 10. Log audit, send notification, publish event               │
└─────────────────────────────────────────────────────────────┘
```

## Email Verification Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 Registration creates user                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Generate verification token                              │
│  2. Store EmailVerificationToken with expiry                   │
│  3. Send verification email                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   EmailVerificationRequest                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Find valid unused token by hash                          │
│  2. Set user.email_verified_at                               │
│  3. If PENDING_VERIFICATION → set status to ACTIVE            │
│  4. Mark token used                                          │
│  5. Log audit, publish EmailVerified event                   │
└─────────────────────────────────────────────────────────────┘

Resend endpoint available for unverified users (same flow, same response).
```

## Security Considerations

### Zero Trust Principles

1. **Never trust, always verify**: Every request validates the session token
2. **Least privilege**: RBAC permissions are scoped to organization
3. **Explicit deny**: Blocked account statuses override all access
4. **Audit all access**: Every auth event creates an immutable audit trail

### Password Security

- **Passlib bcrypt** with configurable rounds (default 12)
- **Automatic salt generation** via bcrypt
- **Timing attack resistance** via Passlib constant-time comparison
- **Password history** prevents reuse of last N passwords
- **Upgrade path** via `needs_update()` method for algorithm changes

### Token Security

- **HMAC-SHA256** hashing for token storage
- **Cryptographically random** token generation via `secrets.token_urlsafe`
- **Configurable expiration** (default: 24h for email, 30m for password reset)
- **Single-use tokens** - marked used after consumption

### Session Management

- **Server-side session persistence** - tokens validated against database
- **Device fingerprinting** - track login device
- **Remember Me** - extended session TTL (30 days default)
- **IP/User-Agent logging** - for audit and anomaly detection
- **Immediate revocation** on logout, password change, or lockout

### Lockout Policy

- **Configurable threshold** (default: 5 attempts)
- **Configurable duration** (default: 15 minutes)
- **Automatic unlock** after lockout period expires

## Folder Structure

| Folder | Purpose |
|--------|---------|
| `schemas/` | Pydantic v2 request/response models with validation |
| `services/` | Business logic orchestration (Application Layer) |
| `repositories/` | Data persistence interfaces and implementations |
| `validators/` | Input and policy validation logic |
| `policies/` | Authorization decision rules |
| `exceptions/` | Custom exception hierarchy |
| `audit/` | Audit log writing utilities |
| `events/` | Domain events for integration |
| `helpers/` | Cross-cutting utilities (hashing, tokens, time) |
| `middleware/` | Framework integration (Streamlit context) |
| `decorators/` | Presentation layer access control |
| `permissions/` | RBAC primitives |
| `constants/` | Default values and configuration |

## Extension Points

### OAuth/SSO Integration

Add new providers in `authentication/services/providers.py`:

```python
class OAuthProvider(Protocol):
    def authenticate(self, token: str) -> OAuthUser: ...
    def get_or_create_user(self, oauth_user: OAuthUser) -> User: ...

class GoogleOAuthProvider:
    def authenticate(self, token: str) -> OAuthUser:
        # Verify Google ID token
        ...
```

### Custom Email Providers

Implement the `EmailProvider` protocol:

```python
class SMTPEmailProvider:
    def send_verification_email(self, email: str, token: str, full_name: str) -> None:
        # Send via SMTP
        ...
```

### Custom Permissions

Extend `AuthPermission` enum in `authentication/permissions/rbac.py`:

```python
class AuthPermission(StrEnum):
    CUSTOM_PERMISSION = "custom.permission"
```

### Password Policy Customization

Override `PasswordPolicy`:

```python
policy = PasswordPolicy(
    min_length=12,
    max_length=256,
    require_uppercase=True,
    require_lowercase=True,
    require_numeric=True,
    require_special=True,
    history_count=10,
    expiration_days=180,
)
```

## Configuration

Environment variables (via `SecuritySettings`):

```bash
SECURITY_SECRET_KEY=your-secret-key-here
SECURITY_PASSWORD_MIN_LENGTH=12
SECURITY_PASSWORD_MAX_LENGTH=128
SECURITY_PASSWORD_REQUIRE_UPPERCASE=true
SECURITY_PASSWORD_REQUIRE_LOWERCASE=true
SECURITY_PASSWORD_REQUIRE_NUMERIC=true
SECURITY_PASSWORD_REQUIRE_SPECIAL=true
SECURITY_PASSWORD_HISTORY_COUNT=5
SECURITY_PASSWORD_EXPIRATION_DAYS=90
SECURITY_BCRYPT_ROUNDS=12
SECURITY_SESSION_TTL_HOURS=24
SECURITY_REMEMBER_ME_TTL_DAYS=30
SECURITY_MAX_LOGIN_ATTEMPTS=5
SECURITY_LOCKOUT_MINUTES=15
SECURITY_EMAIL_VERIFICATION_TOKEN_TTL_HOURS=24
SECURITY_PASSWORD_RESET_TOKEN_TTL_MINUTES=30
SECURITY_USERNAME_UNIQUE=true
SECURITY_REQUIRE_VERIFIED_EMAIL=true
```

## Database Models

Key models in `database/models/auth.py`:

- `User` - Core user entity with status, password hash, lockout fields
- `UserProfile` - Extended profile information
- `UserSession` - Active login sessions
- `LoginHistory` - Immutable login audit trail
- `PasswordResetToken` - One-time password reset tokens
- `EmailVerificationToken` - Email verification tokens
- `PasswordHistory` - Historical password hashes
- `TwoFactorAuth` - 2FA configuration
- `UserPreference` - User-level preferences
- `OAuthAccount` - Linked OAuth provider accounts

## Usage Examples

### Registration

```python
from authentication import RegistrationService
from authentication.schemas import RegisterOrganizationRequest, UserProfileInput

service = RegistrationService()
response = service.register_organization(
    RegisterOrganizationRequest(
        email="user@example.com",
        password="StrongP@ss123",
        organization_name="Acme Corp",
        profile=UserProfileInput(full_name="Test User"),
    )
)
```

### Login

```python
from authentication import AuthenticationService
from authentication.schemas import LoginRequest

service = AuthenticationService()
response = service.login(
    LoginRequest(
        identifier="user@example.com",
        password="StrongP@ss123",
        organization_slug="acme-corp",
        remember_me=False,
    )
)
# Use response.session.session_token for authenticated requests
```

### Session Validation (Streamlit)

```python
from authentication.middleware import SessionMiddleware

middleware = SessionMiddleware()
context = middleware.authenticate_token(st.session_state.token)
# context.user_id, context.organization_id, context.permissions
```

### Permission Check

```python
from authentication.decorators import require_permission
from authentication.permissions import AuthPermission

@require_permission(AuthPermission.USERS_WRITE)
def update_user(user: User, request: UpdateUserRequest, permissions: set[str]):
    ...
```