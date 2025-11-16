"""
Async OAuth2 client implementation.
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


class AsyncOAuth2Client:
    """
    Async OAuth 2.0 client for handling authentication flows.

    This client provides async/await support for OAuth 2.0 operations,
    perfect for use with FastAPI, aiohttp, and other async frameworks.

    Example:
        ```python
        from pauth.async_client import AsyncOAuth2Client
        from pauth import Providers

        async def login():
            client = AsyncOAuth2Client(
                provider=Providers.GOOGLE,
                client_id="your_client_id",
                client_secret="your_client_secret",
                redirect_uri="https://your-app.com/callback"
            )

            # Get authorization URL (sync)
            auth_url = client.get_authorization_url(scope=["openid", "email"])

            # Exchange code for tokens (async)
            tokens = await client.exchange_code_async(code="auth_code", state="state")

            # Get user info (async)
            user_info = await client.get_user_info_async(tokens.access_token)
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
        Initialize the async OAuth2 client.

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

        Note: This method is synchronous as it only generates a URL.

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

    async def exchange_code_async(
        self,
        code: str,
        state: Optional[str] = None,
        validate_state: bool = True
    ) -> TokenResponse:
        """
        Async: Exchange authorization code for access token.

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
            # Import async request utility
            from src.utils.async_request import make_async_request

            # Prepare token exchange request
            if self.use_pkce and hasattr(self.provider, 'exchange_code_for_access_token_pkce'):
                if not self._code_verifier:
                    raise AuthorizationError("PKCE enabled but no code verifier available")

                # PKCE token exchange
                headers = self.provider._get_authorization_header() \
                    if hasattr(self.provider, '_get_authorization_header') else {}

                data = {
                    'code': code,
                    'grant_type': 'authorization_code',
                    'client_id': self.client_id,
                    'redirect_uri': self.redirect_uri,
                    'code_verifier': self._code_verifier
                }

                token_data = await make_async_request(
                    'POST',
                    self.provider.token_endpoint,
                    headers=headers,
                    data=data
                )
            else:
                # Standard token exchange
                data = {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'code': code,
                    'redirect_uri': self.redirect_uri,
                    'grant_type': 'authorization_code'
                }

                token_data = await make_async_request(
                    'POST',
                    self.provider.token_endpoint,
                    data=data
                )

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

    async def get_user_info_async(self, access_token: str) -> UserInfo:
        """
        Async: Fetch user information using the access token.

        Args:
            access_token: Valid access token

        Returns:
            UserInfo: User information from the provider

        Raises:
            UserInfoError: If fetching user info fails
        """
        if not hasattr(self.provider, 'user_info_endpoint'):
            raise UserInfoError(
                f"{self.provider.__class__.__name__} does not support user info retrieval"
            )

        try:
            from src.utils.async_request import make_async_request

            headers = {'Authorization': f'Bearer {access_token}'}

            user_data = await make_async_request(
                'GET',
                self.provider.user_info_endpoint,
                headers=headers
            )

            if not user_data:
                raise UserInfoError("Provider returned empty user info response")

            return UserInfo.from_dict(user_data)

        except Exception as e:
            if isinstance(e, UserInfoError):
                raise
            raise UserInfoError(f"Failed to fetch user info: {e}")

    async def refresh_token_async(self, refresh_token: str) -> TokenResponse:
        """
        Async: Refresh an access token using a refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            TokenResponse: New token response

        Raises:
            TokenError: If token refresh fails
        """
        if not hasattr(self.provider, 'token_endpoint'):
            raise TokenError(
                f"{self.provider.__class__.__name__} does not support token refresh"
            )

        try:
            from src.utils.async_request import make_async_request

            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }

            token_data = await make_async_request(
                'POST',
                self.provider.token_endpoint,
                data=data
            )

            if not token_data:
                raise TokenError("Provider returned empty token response")

            return TokenResponse.from_dict(token_data)

        except Exception as e:
            if isinstance(e, TokenError):
                raise
            raise TokenError(f"Failed to refresh token: {e}")

    async def revoke_token_async(self, token: str) -> bool:
        """
        Async: Revoke an access or refresh token.

        Args:
            token: Token to revoke

        Returns:
            bool: True if revocation was successful

        Raises:
            TokenError: If token revocation fails
        """
        if not hasattr(self.provider, 'revocation_endpoint'):
            raise TokenError(
                f"{self.provider.__class__.__name__} does not support token revocation"
            )

        try:
            from src.utils.async_request import make_async_request

            data = {'token': token}

            result = await make_async_request(
                'POST',
                self.provider.revocation_endpoint,
                data=data
            )

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
