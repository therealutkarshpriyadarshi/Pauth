"""
Discord OAuth 2.0 provider implementation.
"""

from src.utils import make_request, OAuthError
from .base import BaseProvider


class DiscordProvider(BaseProvider):
    """
    Discord OAuth 2.0 provider implementation.

    Supports:
    - Authorization code flow
    - Token exchange
    - Token refresh
    - Token revocation
    - User info retrieval
    """

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scopes=None):
        """
        Initialize Discord OAuth provider.

        Args:
            client_id: Discord OAuth client ID
            client_secret: Discord OAuth client secret
            redirect_uri: Registered redirect URI
            scopes: List of scopes (defaults to identify, email)
        """
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scopes=scopes or ['identify', 'email']
        )
        self.authorization_endpoint = "https://discord.com/api/oauth2/authorize"
        self.token_endpoint = "https://discord.com/api/oauth2/token"
        self.revocation_endpoint = "https://discord.com/api/oauth2/token/revoke"
        self.user_info_endpoint = "https://discord.com/api/users/@me"

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

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = make_request('POST', self.token_endpoint, headers=headers, data=data)

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

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = make_request('POST', self.token_endpoint, headers=headers, data=data)

        if response:
            return response
        else:
            raise OAuthError("Failed to refresh token")

    def revoke_token(self, token: str) -> dict:
        """
        Revoke an access token.

        Args:
            token: Token to revoke

        Returns:
            dict: Revocation response

        Raises:
            OAuthError: If token revocation fails
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'token': token
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = make_request('POST', self.revocation_endpoint, headers=headers, data=data)

        if response is not None:
            return response
        else:
            raise OAuthError("Failed to revoke token")

    def get_user_info(self, access_token: str) -> dict:
        """
        Fetch user information.

        Args:
            access_token: Valid access token

        Returns:
            dict: User information

        Raises:
            OAuthError: If fetching user info fails
        """
        headers = {'Authorization': f'Bearer {access_token}'}

        response = make_request('GET', self.user_info_endpoint, headers=headers)

        if response:
            return response
        else:
            raise OAuthError("Failed to fetch user info")
