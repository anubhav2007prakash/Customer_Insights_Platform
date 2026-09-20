"""Time-based One-Time Password (TOTP) for authenticator apps.

Supports:
- TOTP generation and verification (RFC 6238)
- QR code generation for mobile authenticator apps
- Recovery codes as backup
- Device naming and management
"""

from __future__ import annotations

import secrets
import string
import qrcode
import io
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from core.config.settings import Settings, get_settings
from core.exceptions.base import ValidationError
from authentication.helpers import utc_now


class TOTPConfig(BaseModel):
    """TOTP configuration (RFC 6238)."""
    
    # TOTP parameters
    time_step: int = Field(default=30)  # seconds
    digits: int = Field(default=6)  # 6-digit codes
    algorithm: str = Field(default="SHA1")  # SHA1, SHA256, SHA512
    
    # Tolerance (allow codes from adjacent time windows)
    window_size: int = Field(default=1)  # Allow ±1 time step


class TOTPSecretModel(BaseModel):
    """TOTP secret record."""
    
    id: UUID
    user_id: UUID
    
    secret_key: str  # Base32-encoded secret
    algorithm: str
    digits: int
    period: int
    
    device_name: str  # e.g., "Google Authenticator (iPhone)"
    
    enabled_at: Optional[datetime] = None
    disabled_at: Optional[datetime] = None
    is_verified: bool = False  # Require verification before enabling
    
    last_used_at: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime


class TOTPService:
    """Time-based One-Time Password service.
    
    Implements RFC 6238 TOTP for use with authenticator apps.
    """
    
    def __init__(
        self,
        config: TOTPConfig | None = None,
        *,
        settings: Settings | None = None,
    ):
        self.config = config or TOTPConfig()
        self.settings = settings or get_settings()
        self._ensure_pyotp()
    
    def _ensure_pyotp(self) -> None:
        """Ensure pyotp is available."""
        try:
            import pyotp
        except ImportError:
            raise ImportError(
                "pyotp is required for TOTP support. "
                "Install with: pip install pyotp"
            )
    
    def generate_secret(self, user_id: UUID, device_name: str = "Authenticator") -> TOTPSecretModel:
        """Generate a new TOTP secret for a user.
        
        Args:
            user_id: User ID
            device_name: Name of the authenticator device/app
        
        Returns:
            TOTPSecretModel with secret and metadata
        """
        import pyotp
        
        # Generate random secret
        secret = pyotp.random_base32()
        now = utc_now()
        
        return TOTPSecretModel(
            id=uuid4(),
            user_id=user_id,
            secret_key=secret,
            algorithm=self.config.algorithm,
            digits=self.config.digits,
            period=self.config.time_step,
            device_name=device_name,
            is_verified=False,  # Must be verified before enabling
            created_at=now,
            updated_at=now,
        )
    
    def get_qr_code(
        self,
        secret_model: TOTPSecretModel,
        account_name: str,
        issuer: str = "InsightForge AI",
    ) -> tuple[str, bytes]:
        """Generate QR code for mobile authenticator setup.
        
        Args:
            secret_model: TOTP secret model
            account_name: User's account name (email)
            issuer: Organization name (shows in authenticator)
        
        Returns:
            Tuple of (otpauth_url, qr_code_png_bytes)
        """
        import pyotp
        
        # Create provisioning URL
        totp = pyotp.TOTP(secret_model.secret_key)
        uri = totp.provisioning_uri(
            name=account_name,
            issuer_name=issuer,
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        png_bytes = io.BytesIO()
        img.save(png_bytes, format="PNG")
        png_bytes.seek(0)
        
        return uri, png_bytes.getvalue()
    
    def verify(
        self,
        secret_model: TOTPSecretModel,
        code: str,
    ) -> bool:
        """Verify a TOTP code.
        
        Args:
            secret_model: TOTP secret model
            code: 6-digit code from authenticator
        
        Returns:
            True if valid, False otherwise
        """
        import pyotp
        
        totp = pyotp.TOTP(
            secret_model.secret_key,
            interval=secret_model.period,
            digits=secret_model.digits,
        )
        
        # Verify with tolerance for clock skew
        return totp.verify(code, valid_window=self.config.window_size)
    
    def verify_initial_setup(
        self,
        secret_model: TOTPSecretModel,
        code: str,
    ) -> bool:
        """Verify TOTP during initial setup.
        
        Requires 2 consecutive valid codes to prevent clock skew issues.
        """
        import pyotp
        
        totp = pyotp.TOTP(
            secret_model.secret_key,
            interval=secret_model.period,
            digits=secret_model.digits,
        )
        
        # Check current and next code
        return totp.verify(code, valid_window=self.config.window_size)


class BackupCodeService:
    """Generate and manage TOTP backup codes.
    
    Backup codes allow account recovery if authenticator is lost.
    """
    
    def __init__(
        self,
        code_count: int = 10,
        code_length: int = 8,
    ):
        self.code_count = code_count
        self.code_length = code_length
    
    def generate(self, user_id: UUID) -> tuple[list[str], dict]:
        """Generate backup codes.
        
        Args:
            user_id: User ID
        
        Returns:
            Tuple of (codes_list, hashed_dict_for_storage)
        """
        codes = []
        for _ in range(self.code_count):
            # Format: XXXX-XXXX (8 random characters with dash)
            code = "-".join([
                self._random_code(4),
                self._random_code(4),
            ])
            codes.append(code)
        
        return codes, {"codes": [self._hash_code(c) for c in codes]}
    
    def verify(
        self,
        provided_code: str,
        stored_hashes: list[str],
    ) -> bool:
        """Verify a backup code against stored hashes.
        
        Args:
            provided_code: Code entered by user
            stored_hashes: List of hashed backup codes
        
        Returns:
            True if code is valid, False otherwise
        """
        provided_hash = self._hash_code(provided_code.replace(" ", "").replace("-", ""))
        
        for stored_hash in stored_hashes:
            if self._constant_time_compare(provided_hash, stored_hash):
                return True
        return False
    
    def _random_code(self, length: int) -> str:
        """Generate random alphanumeric code."""
        chars = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))
    
    def _hash_code(self, code: str) -> str:
        """Hash backup code."""
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()
    
    def _constant_time_compare(self, a: str, b: str) -> bool:
        """Constant-time comparison."""
        import hmac
        return hmac.compare_digest(a.encode(), b.encode())


class MFAService:
    """Multi-Factor Authentication orchestration service.
    
    Coordinates Email OTP, TOTP, and backup codes.
    """
    
    def __init__(
        self,
        otp_config: Optional[dict] = None,
        totp_config: Optional[dict] = None,
    ):
        from .otp import OTPService, OTPConfig
        
        self.otp = OTPService(
            config=OTPConfig(**otp_config) if otp_config else OTPConfig()
        )
        self.totp = TOTPService(
            config=TOTPConfig(**totp_config) if totp_config else TOTPConfig()
        )
        self.backup_codes = BackupCodeService()
    
    def get_totp_setup_info(
        self,
        user_id: UUID,
        email: str,
    ) -> dict:
        """Get information for TOTP setup flow.
        
        Returns:
            Dict with QR code, setup URL, and backup codes
        """
        secret_model = self.totp.generate_secret(user_id, "Authenticator App")
        uri, qr_code_png = self.totp.get_qr_code(
            secret_model,
            account_name=email,
        )
        backup_codes, hashed_dict = self.backup_codes.generate(user_id)
        
        return {
            "secret": secret_model.secret_key,
            "setup_uri": uri,
            "qr_code_png": qr_code_png,  # Send as base64 to frontend
            "backup_codes": backup_codes,
            "backup_codes_hashed": hashed_dict,
            "message": "Save these backup codes in a safe place. You'll need them if you lose access to your authenticator.",
        }
