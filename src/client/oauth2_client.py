"""
Main OAuth2 client implementation.
"""

import secrets
from typing import Optional, List, Union

from src.exceptions import (
    ConfigurationError, InvalidStateError, TokenError,
    AuthorizationError, UserInfoError
)
from src.models import Providers, TokenResponse, UserInfo
from src.providers.base import BaseProvider
from src.storage import BaseTokenStorage, MemoryTokenStorage


class OAuth2Client:
    """
    Main OAuth 2.0 client for handling authentication flows.

    This client provides a high-level interface for OAuth 2.0 authentication
    with support for multiple providers, PKCE, and token management.

    Example:
        ```python
        from pauth import OAuth2Client, Providers

        client = OAuth2Client(
            provider=Providers.GOOGLE,
            client_id="your_client_id",
            client_secret="your_client_secret",
            redirect_uri="https://your-app.com/callback"
        )

        # Get authorization URL
        auth_url = client.get_authorization_url(scope=["openid", "email"])

        # Exchange code for tokens
        tokens = client.exchange_code(code="auth_code", state="state_value")

        # Get user info
        user_info = client.get_user_info(tokens.access_token)
        ```
    """

    def __init__(
        self,
        provider: Union[Providers, str, BaseProvider],
        client_id: str,
        client_secret: str = None,
        redirect_uri: str = None,
        scopes: Optional[List[str]] = None,
        use_pkce: bool = False,
        token_storage: Optional[BaseTokenStorage] = None
    ):
        """
        Initialize the OAuth2 client.

        Args:
            provider: OAuth provider (Providers enum, string name, or provider instance)
            client_id: Client ID from the OAuth provider
            client_secret: Client secret from the OAuth provider (not needed for PKCE)
            redirect_uri: Redirect URI registered with the provider
            scopes: List of scopes to request
            use_pkce: Whether to use PKCE (Proof Key for Code Exchange)
            token_storage: Custom token storage backend (defaults to MemoryTokenStorage)

        Raises:
            ConfigurationError: If required configuration is missing
        """
        if not client_id:
            raise ConfigurationError("client_id is required")

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes or []
        self.use_pkce = use_pkce

        # Initialize provider
        if isinstance(provider, BaseProvider):
            self.provider = provider
        elif isinstance(provider, Providers):
            provider_class = provider.get_provider_class()
            self.provider = provider_class(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scopes=scopes
            )
        elif isinstance(provider, str):
            provider_enum = Providers.from_string(provider)
            provider_class = provider_enum.get_provider_class()
            self.provider = provider_class(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scopes=scopes
            )
        else:
            raise ConfigurationError(
                f"Invalid provider type: {type(provider)}. "
                "Must be Providers enum, string, or BaseProvider instance."
            )

        # Initialize storage
        self.token_storage = token_storage or MemoryTokenStorage()

        # PKCE state
        self._code_verifier: Optional[str] = None
        self._state: Optional[str] = None

    def get_authorization_url(
        self,
        scope: Optional[List[str]] = None,
        state: Optional[str] = None,
        **additional_params
    ) -> str:
        """
        Generate the authorization URL for the OAuth flow.

        Args:
            scope: List of scopes (overrides client scopes if provided)
            state: State parameter for CSRF protection (auto-generated if not provided)
            **additional_params: Additional provider-specific parameters

        Returns:
            str: Authorization URL to redirect the user to
        """
        # Use provided scopes or fall back to client scopes
        if scope:
            self.provider.scopes = scope

        # Generate or use provided state
        self._state = state or self.generate_state()

        # Handle PKCE if enabled
        if self.use_pkce:
            self._code_verifier = self._generate_code_verifier()
            code_challenge = self.provider._generate_code_challenge(self._code_verifier) \
                if hasattr(self.provider, '_generate_code_challenge') else \
                self._generate_code_challenge(self._code_verifier)

            additional_params.update({
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256'
            })

        # Get authorization URL from provider
        auth_url = self.provider.prepare_auth_url(additional_params)

        # Override state if we generated our own
        if state or self.use_pkce:
            import re
            auth_url = re.sub(r'state=[^&]*', f'state={self._state}', auth_url)

        return auth_url

    def exchange_code(
        self,
        code: str,
        state: Optional[str] = None,
        validate_state: bool = True
    ) -> TokenResponse:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from the callback
            state: State parameter from the callback
            validate_state: Whether to validate the state parameter

        Returns:
            TokenResponse: Token response with access token and other info

        Raises:
            InvalidStateError: If state validation fails
            AuthorizationError: If code exchange fails
        """
        # Validate state if required
        if validate_state and state:
            if not self._state:
                raise InvalidStateError("No state was stored for validation")
            if state != self._state:
                raise InvalidStateError(
                    "State parameter mismatch. Possible CSRF attack."
                )

        try:
            # Exchange code for token
            if self.use_pkce and hasattr(self.provider, 'exchange_code_for_access_token_pkce'):
                if not self._code_verifier:
                    raise AuthorizationError("PKCE enabled but no code verifier available")
                token_data = self.provider.exchange_code_for_access_token_pkce(
                    code, self._code_verifier
                )
            else:
                token_data = self.provider.exchange_code_for_access_token(code)

            if not token_data:
                raise TokenError("Provider returned empty token response")

            # Convert to TokenResponse
            tokens = TokenResponse.from_dict(token_data)

            # Clear PKCE state
            self._code_verifier = None
            self._state = None

            return tokens

        except Exception as e:
            if isinstance(e, (InvalidStateError, TokenError, AuthorizationError)):
                raise
            raise AuthorizationError(f"Failed to exchange code for token: {e}")

    def get_user_info(self, access_token: str) -> UserInfo:
        """
        Fetch user information using the access token.

        Args:
            access_token: Valid access token

        Returns:
            UserInfo: User information from the provider

        Raises:
            UserInfoError: If fetching user info fails
        """
        if not hasattr(self.provider, 'get_user_info'):
            raise UserInfoError(
                f"{self.provider.__class__.__name__} does not support user info retrieval"
            )

        try:
            user_data = self.provider.get_user_info(access_token)
            if not user_data:
                raise UserInfoError("Provider returned empty user info response")

            return UserInfo.from_dict(user_data)

        except Exception as e:
            if isinstance(e, UserInfoError):
                raise
            raise UserInfoError(f"Failed to fetch user info: {e}")

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh an access token using a refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            TokenResponse: New token response

        Raises:
            TokenError: If token refresh fails
        """
        if not hasattr(self.provider, 'refresh_token'):
            raise TokenError(
                f"{self.provider.__class__.__name__} does not support token refresh"
            )

        try:
            token_data = self.provider.refresh_token(refresh_token)
            if not token_data:
                raise TokenError("Provider returned empty token response")

            return TokenResponse.from_dict(token_data)

        except Exception as e:
            if isinstance(e, TokenError):
                raise
            raise TokenError(f"Failed to refresh token: {e}")

    def revoke_token(self, token: str) -> bool:
        """
        Revoke an access or refresh token.

        Args:
            token: Token to revoke

        Returns:
            bool: True if revocation was successful

        Raises:
            TokenError: If token revocation fails
        """
        if not hasattr(self.provider, 'revoke_token'):
            raise TokenError(
                f"{self.provider.__class__.__name__} does not support token revocation"
            )

        try:
            result = self.provider.revoke_token(token)
            return result is not None

        except Exception as e:
            raise TokenError(f"Failed to revoke token: {e}")

    @staticmethod
    def generate_state() -> str:
        """
        Generate a random state parameter for CSRF protection.

        Returns:
            str: Random state string
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def _generate_code_verifier() -> str:
        """
        Generate a code verifier for PKCE.

        Returns:
            str: Random code verifier
        """
        return secrets.token_urlsafe(64)

    @staticmethod
    def _generate_code_challenge(code_verifier: str) -> str:
        """
        Generate a code challenge from a code verifier.

        Args:
            code_verifier: Code verifier string

        Returns:
            str: Base64-encoded SHA256 hash of the verifier
        """
        import hashlib
        import base64

        verifier_bytes = code_verifier.encode('utf-8')
        sha256_hash = hashlib.sha256(verifier_bytes).digest()
        base64_encoded = base64.urlsafe_b64encode(sha256_hash).decode('utf-8')
        return base64_encoded.rstrip('=')
