"""
Apple Sign In OAuth 2.0 provider implementation.
"""

from src.utils import make_request, OAuthError
from .base import BaseProvider


class AppleProvider(BaseProvider):
    """
    Apple Sign In OAuth 2.0 provider implementation.

    Supports:
    - Authorization code flow
    - Token exchange
    - Token refresh
    - Token revocation

    Note: Apple Sign In requires special JWT handling for client authentication.
    This is a basic implementation. For production use, you'll need to implement
    client_secret generation using JWT with your Apple private key.
    """

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scopes=None):
        """
        Initialize Apple OAuth provider.

        Args:
            client_id: Apple Service ID (client_id)
            client_secret: Generated JWT (or Team ID for client secret)
            redirect_uri: Registered redirect URI
            scopes: List of scopes (defaults to name, email)
        """
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scopes=scopes or ['name', 'email']
        )
        self.authorization_endpoint = "https://appleid.apple.com/auth/authorize"
        self.token_endpoint = "https://appleid.apple.com/auth/token"
        self.revocation_endpoint = "https://appleid.apple.com/auth/revoke"

    def exchange_code_for_access_token(self, code: str, **kwargs) -> dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from callback
            **kwargs: Additional parameters

        Returns:
            dict: Token response

        Raises:
            OAuthError: If token exchange fails
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }

        response = make_request('POST', self.token_endpoint, data=data)

        if response:
            return response
        else:
            raise OAuthError("Failed to exchange code for access token")

    def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh an access token.

        Args:
            refresh_token: Refresh token

        Returns:
            dict: New token response

        Raises:
            OAuthError: If token refresh fails
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        response = make_request('POST', self.token_endpoint, data=data)

        if response:
            return response
        else:
            raise OAuthError("Failed to refresh token")

    def revoke_token(self, token: str, token_type_hint: str = 'access_token') -> dict:
        """
        Revoke an access or refresh token.

        Args:
            token: Token to revoke
            token_type_hint: Type of token (access_token or refresh_token)

        Returns:
            dict: Revocation response

        Raises:
            OAuthError: If token revocation fails
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'token': token,
            'token_type_hint': token_type_hint
        }

        response = make_request('POST', self.revocation_endpoint, data=data)

        if response is not None:
            return response
        else:
            raise OAuthError("Failed to revoke token")
