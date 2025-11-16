"""
Django integration for PAuth OAuth 2.0.
"""

from typing import Union, Optional, List

try:
    from django.conf import settings
    from django.shortcuts import redirect
    from django.http import HttpRequest, HttpResponse
except ImportError:
    raise ImportError(
        "Django is required for Django integration. "
        "Install it with: pip install pauth[django]"
    )

from src.client import OAuth2Client
from src.models import Providers, TokenResponse, UserInfo
from src.exceptions import InvalidStateError, AuthorizationError, ConfigurationError


class DjangoOAuth:
    """
    Django integration for OAuth 2.0 authentication.

    Example:
        ```python
        # settings.py
        PAUTH_CONFIG = {
            'google': {
                'client_id': 'your-client-id',
                'client_secret': 'your-client-secret',
                'redirect_uri': 'http://localhost:8000/oauth/callback',
                'scopes': ['openid', 'email', 'profile']
            }
        }

        # views.py
        from pauth.integrations.django import DjangoOAuth

        oauth = DjangoOAuth(provider='google')

        def login(request):
            return oauth.authorize_redirect(request)

        def callback(request):
            tokens = oauth.authorize_access_token(request)
            user_info = oauth.get_user_info(tokens.access_token)
            return HttpResponse(f"Welcome, {user_info.name}!")
        ```
    """

    def __init__(
        self,
        provider: Union[Providers, str],
        client_id: str = None,
        client_secret: str = None,
        redirect_uri: str = None,
        scopes: Optional[List[str]] = None,
        use_pkce: bool = False
    ):
        """
        Initialize Django OAuth integration.

        Args:
            provider: OAuth provider (Providers enum or string)
            client_id: OAuth client ID (loaded from settings if not provided)
            client_secret: OAuth client secret (loaded from settings if not provided)
            redirect_uri: Redirect URI (loaded from settings if not provided)
            scopes: List of OAuth scopes (loaded from settings if not provided)
            use_pkce: Whether to use PKCE
        """
        self.provider_name = provider if isinstance(provider, str) else provider.value

        # Load from Django settings if not provided
        config = self._load_config()

        self.client_id = client_id or config.get('client_id')
        self.client_secret = client_secret or config.get('client_secret')
        self.redirect_uri = redirect_uri or config.get('redirect_uri')
        self.scopes = scopes or config.get('scopes')
        self.use_pkce = use_pkce or config.get('use_pkce', False)

        if not self.client_id or not self.client_secret:
            raise ConfigurationError(
                f"client_id and client_secret are required for {self.provider_name}"
            )

        self._client: Optional[OAuth2Client] = None

    def _load_config(self) -> dict:
        """
        Load configuration from Django settings.

        Returns:
            dict: Provider configuration
        """
        pauth_config = getattr(settings, 'PAUTH_CONFIG', {})

        if self.provider_name not in pauth_config:
            return {}

        return pauth_config[self.provider_name]

    @property
    def client(self) -> OAuth2Client:
        """
        Get or create the OAuth2Client instance.

        Returns:
            OAuth2Client: OAuth client instance
        """
        if self._client is None:
            self._client = OAuth2Client(
                provider=self.provider_name,
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scopes=self.scopes,
                use_pkce=self.use_pkce
            )
        return self._client

    def authorize_redirect(
        self,
        request: HttpRequest,
        scope: Optional[List[str]] = None,
        **kwargs
    ) -> HttpResponse:
        """
        Redirect to the OAuth provider's authorization page.

        Args:
            request: Django HTTP request
            scope: OAuth scopes to request (overrides default)
            **kwargs: Additional parameters

        Returns:
            Django redirect response
        """
        # Generate authorization URL
        auth_url = self.client.get_authorization_url(scope=scope, **kwargs)

        # Store state in session for validation
        if hasattr(self.client, '_state') and self.client._state:
            request.session['oauth_state'] = self.client._state

        # Store PKCE verifier in session if using PKCE
        if self.use_pkce and hasattr(self.client, '_code_verifier') and self.client._code_verifier:
            request.session['oauth_code_verifier'] = self.client._code_verifier

        return redirect(auth_url)

    def authorize_access_token(self, request: HttpRequest) -> TokenResponse:
        """
        Handle the OAuth callback and exchange code for tokens.

        Args:
            request: Django HTTP request

        Returns:
            TokenResponse: OAuth tokens

        Raises:
            InvalidStateError: If state validation fails
            AuthorizationError: If authorization fails
        """
        # Get code and state from request
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')

        if error:
            raise AuthorizationError(f"Authorization failed: {error}")

        if not code:
            raise AuthorizationError("No authorization code received")

        # Validate state
        stored_state = request.session.get('oauth_state')
        if stored_state and state != stored_state:
            raise InvalidStateError("State parameter mismatch")

        # Restore PKCE verifier if using PKCE
        if self.use_pkce:
            code_verifier = request.session.get('oauth_code_verifier')
            if code_verifier:
                self.client._code_verifier = code_verifier

        # Exchange code for tokens
        tokens = self.client.exchange_code(code, state=state)

        # Clean up session
        request.session.pop('oauth_state', None)
        request.session.pop('oauth_code_verifier', None)

        return tokens

    def get_user_info(self, access_token: str) -> UserInfo:
        """
        Fetch user information using an access token.

        Args:
            access_token: Valid access token

        Returns:
            UserInfo: User information
        """
        return self.client.get_user_info(access_token)
