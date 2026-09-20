"""OAuth provider abstractions and framework.

Supports:
- Google OAuth
- Microsoft OAuth (Azure AD, Microsoft Account)
- GitHub OAuth
- Extensible framework for other providers
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


@dataclass
class OAuthUserInfo:
    """User information from OAuth provider."""
    
    provider_id: str  # "google", "microsoft", "github"
    provider_user_id: str  # User ID from provider
    email: str
    email_verified: bool
    full_name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture_url: Optional[str] = None
    locale: Optional[str] = None
    phone_number: Optional[str] = None
    
    # Provider-specific metadata
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class OAuthAccessToken:
    """OAuth access token info."""
    
    access_token: str
    token_type: str  # "Bearer"
    expires_in: int  # seconds
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scope: Optional[str] = None
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class OAuthProvider(ABC):
    """Abstract base for OAuth providers."""
    
    @abstractmethod
    def get_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        scopes: Optional[list[str]] = None,
    ) -> str:
        """Get OAuth authorization URL.
        
        Args:
            redirect_uri: Callback URL after authorization
            state: CSRF protection token
            scopes: List of scopes to request
        
        Returns:
            Authorization URL for browser redirect
        """
        pass
    
    @abstractmethod
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str,
    ) -> OAuthAccessToken:
        """Exchange authorization code for access token.
        
        Args:
            code: Authorization code from provider
            redirect_uri: Must match initial request
        
        Returns:
            OAuthAccessToken
        """
        pass
    
    @abstractmethod
    async def get_user_info(
        self,
        access_token: str,
    ) -> OAuthUserInfo:
        """Get user information from access token.
        
        Args:
            access_token: OAuth access token
        
        Returns:
            OAuthUserInfo
        """
        pass
    
    @abstractmethod
    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> OAuthAccessToken:
        """Refresh an expired access token.
        
        Args:
            refresh_token: Refresh token from initial authorization
        
        Returns:
            New OAuthAccessToken
        """
        pass
    
    @abstractmethod
    def get_revoke_url(self, access_token: str) -> str:
        """Get URL to revoke token access."""
        pass


class OAuthAccount(BaseModel):
    """User's linked OAuth account."""
    
    id: UUID
    user_id: UUID
    
    provider: str  # "google", "microsoft", "github"
    provider_user_id: str  # User ID from provider
    email: str
    email_verified: bool
    full_name: Optional[str] = None
    picture_url: Optional[str] = None
    
    access_token: str  # Encrypted
    refresh_token: Optional[str] = None  # Encrypted
    token_expires_at: Optional[datetime] = None
    
    linked_at: datetime
    last_used_at: Optional[datetime] = None
    is_active: bool = True
    
    metadata: dict = Field(default_factory=dict)


class OAuthService:
    """OAuth service for managing multiple providers."""
    
    def __init__(self):
        self.providers: dict[str, OAuthProvider] = {}
    
    def register_provider(self, name: str, provider: OAuthProvider) -> None:
        """Register an OAuth provider.
        
        Args:
            name: Provider name ("google", "microsoft", etc.)
            provider: OAuth provider implementation
        """
        self.providers[name] = provider
    
    def get_provider(self, name: str) -> OAuthProvider:
        """Get registered provider.
        
        Args:
            name: Provider name
        
        Returns:
            OAuthProvider
            
        Raises:
            KeyError: If provider not registered
        """
        if name not in self.providers:
            raise KeyError(f"OAuth provider '{name}' not registered")
        return self.providers[name]
    
    def get_authorization_url(
        self,
        provider_name: str,
        redirect_uri: str,
        state: str,
        scopes: Optional[list[str]] = None,
    ) -> str:
        """Get authorization URL for provider."""
        provider = self.get_provider(provider_name)
        return provider.get_authorization_url(redirect_uri, state, scopes)
    
    async def exchange_code_for_token(
        self,
        provider_name: str,
        code: str,
        redirect_uri: str,
    ) -> OAuthAccessToken:
        """Exchange authorization code for token."""
        provider = self.get_provider(provider_name)
        return await provider.exchange_code_for_token(code, redirect_uri)
    
    async def get_user_info(
        self,
        provider_name: str,
        access_token: str,
    ) -> OAuthUserInfo:
        """Get user info from provider."""
        provider = self.get_provider(provider_name)
        return await provider.get_user_info(access_token)
    
    async def refresh_token(
        self,
        provider_name: str,
        refresh_token: str,
    ) -> OAuthAccessToken:
        """Refresh access token."""
        provider = self.get_provider(provider_name)
        return await provider.refresh_access_token(refresh_token)
