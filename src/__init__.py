"""
PAuth - Making OAuth 2.0 Authentication Simple

A modern Python library for OAuth 2.0 authentication with multiple providers.

Features:
- 🔐 Complete OAuth 2.0 implementation with PKCE support
- 🌐 8+ OAuth providers (Google, GitHub, Facebook, Twitter, etc.)
- ⚡ Async/await support for modern Python frameworks
- 🛡️ Built-in security scanner
- 📊 Analytics and monitoring
- 🎨 Interactive testing playground
- 🔧 Flask & Django integrations
"""

__version__ = "0.2.0"

# Core client
from .client import OAuth2Client

# Models
from .models import Providers, TokenResponse, UserInfo

# Storage
from .storage import BaseTokenStorage, MemoryTokenStorage, FileTokenStorage

# Exceptions
from .exceptions import (
    PAuthError,
    AuthorizationError,
    TokenError,
    InvalidStateError,
    ProviderError,
    ConfigurationError,
    TokenStorageError,
    PKCEError,
    ScopeError,
    UserInfoError,
    OAuthError  # Backwards compatibility
)

# Optional features (require additional dependencies)

# Async support (requires: aiohttp)
try:
    from .async_client import AsyncOAuth2Client
    _has_async = True
except ImportError:
    AsyncOAuth2Client = None
    _has_async = False

# Security scanner (requires: rich)
try:
    from .security import SecurityAuditor, SecurityReport, SecurityReporter
    _has_security = True
except ImportError:
    SecurityAuditor = SecurityReport = SecurityReporter = None
    _has_security = False

# Analytics (requires: rich)
try:
    from .analytics import OAuthAnalytics, AnalyticsDashboard
    _has_analytics = True
except ImportError:
    OAuthAnalytics = AnalyticsDashboard = None
    _has_analytics = False

# Playground (requires: rich, qrcode)
try:
    from .playground import OAuthPlayground
    _has_playground = True
except ImportError:
    OAuthPlayground = None
    _has_playground = False


__all__ = [
    # Version
    '__version__',

    # Core
    'OAuth2Client',

    # Models
    'Providers',
    'TokenResponse',
    'UserInfo',

    # Storage
    'BaseTokenStorage',
    'MemoryTokenStorage',
    'FileTokenStorage',

    # Exceptions
    'PAuthError',
    'AuthorizationError',
    'TokenError',
    'InvalidStateError',
    'ProviderError',
    'ConfigurationError',
    'TokenStorageError',
    'PKCEError',
    'ScopeError',
    'UserInfoError',
    'OAuthError',

    # Optional features
    'AsyncOAuth2Client',  # Async support
    'SecurityAuditor',  # Security scanner
    'SecurityReport',
    'SecurityReporter',
    'OAuthAnalytics',  # Analytics
    'AnalyticsDashboard',
    'OAuthPlayground',  # Interactive playground
]


def get_version():
    """Get PAuth version."""
    return __version__


def check_features():
    """
    Check which optional features are available.

    Returns:
        dict: Dictionary of feature availability
    """
    return {
        'async_support': _has_async,
        'security_scanner': _has_security,
        'analytics': _has_analytics,
        'playground': _has_playground
    }


def print_features():
    """Print available features."""
    features = check_features()

    print(f"PAuth v{__version__}")
    print("\nCore Features:")
    print("  ✓ OAuth2Client - OAuth 2.0 authentication")
    print("  ✓ 8+ OAuth Providers (Google, GitHub, Facebook, etc.)")
    print("  ✓ Token storage (Memory, File)")
    print("  ✓ Flask & Django integrations")

    print("\nOptional Features:")
    print(f"  {'✓' if features['async_support'] else '✗'} Async/Await Support (requires: aiohttp)")
    print(f"  {'✓' if features['security_scanner'] else '✗'} Security Scanner (requires: rich)")
    print(f"  {'✓' if features['analytics'] else '✗'} Analytics Dashboard (requires: rich)")
    print(f"  {'✓' if features['playground'] else '✗'} Interactive Playground (requires: rich, qrcode)")

    if not all(features.values()):
        print("\nTo install all features:")
        print("  pip install pauth[all]")
        print("\nOr install specific features:")
        if not features['async_support']:
            print("  pip install aiohttp  # For async support")
        if not features['security_scanner'] or not features['analytics'] or not features['playground']:
            print("  pip install rich     # For security, analytics, and playground")
        if not features['playground']:
            print("  pip install qrcode   # For playground QR codes")
