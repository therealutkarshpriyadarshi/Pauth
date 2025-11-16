"""
Microsoft OAuth 2.0 provider implementation.
"""

from src.utils import make_request, OAuthError
from .base import BaseProvider


class MicrosoftProvider(BaseProvider):
    """
    Microsoft OAuth 2.0 provider implementation.

    Supports:
    - Authorization code flow
    - Token exchange
    - Token refresh
    - Token revocation
    - User info retrieval
    """

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scopes=None, tenant='common'):
        """
        Initialize Microsoft OAuth provider.

        Args:
            client_id: Microsoft OAuth client ID
            client_secret: Microsoft OAuth client secret
            redirect_uri: Registered redirect URI
            scopes: List of scopes (defaults to openid, email, profile)
            tenant: Azure AD tenant ID (defaults to 'common' for multi-tenant)
        """
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scopes=scopes or ['openid', 'email', 'profile']
        )
        self.tenant = tenant
        self.authorization_endpoint = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
        self.token_endpoint = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
        self.revocation_endpoint = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/logout"
        self.user_info_endpoint = "https://graph.microsoft.com/v1.0/me"

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
