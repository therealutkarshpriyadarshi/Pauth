"""
Flask integration for PAuth OAuth 2.0.
"""

from typing import Union, Optional, List
from urllib.parse import urlencode

try:
    from flask import redirect, request, session, url_for
except ImportError:
    raise ImportError(
        "Flask is required for Flask integration. "
        "Install it with: pip install pauth[flask]"
    )

from src.client import OAuth2Client
from src.models import Providers, TokenResponse, UserInfo
from src.exceptions import InvalidStateError, AuthorizationError


class FlaskOAuth:
    """
    Flask integration for OAuth 2.0 authentication.

    Provides a simple interface for handling OAuth flows in Flask applications.

    Example:
        ```python
        from flask import Flask
        from pauth.integrations.flask import FlaskOAuth

        app = Flask(__name__)
        app.secret_key = 'your-secret-key'

        oauth = FlaskOAuth(
            app=app,
            provider='google',
            client_id='your-client-id',
            client_secret='your-client-secret',
            redirect_uri='http://localhost:5000/callback'
        )

        @app.route('/login')
        def login():
            return oauth.authorize_redirect()

        @app.route('/callback')
        def callback():
            tokens = oauth.authorize_access_token()
            user_info = oauth.get_user_info(tokens.access_token)
            return f"Welcome, {user_info.name}!"
        ```
    """

    def __init__(
        self,
        app=None,
        provider: Union[Providers, str] = None,
        client_id: str = None,
        client_secret: str = None,
        redirect_uri: str = None,
        scopes: Optional[List[str]] = None,
        use_pkce: bool = False
    ):
        """
        Initialize Flask OAuth integration.

        Args:
            app: Flask application instance
            provider: OAuth provider (Providers enum or string)
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: Redirect URI
            scopes: List of OAuth scopes
            use_pkce: Whether to use PKCE
        """
        self.app = app
        self.provider = provider
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.use_pkce = use_pkce

        self._client: Optional[OAuth2Client] = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize the extension with a Flask app.

        Args:
            app: Flask application instance
        """
        self.app = app

        # Load config from app if not provided
        if not self.client_id:
            self.client_id = app.config.get('PAUTH_CLIENT_ID')
        if not self.client_secret:
            self.client_secret = app.config.get('PAUTH_CLIENT_SECRET')
        if not self.redirect_uri:
            self.redirect_uri = app.config.get('PAUTH_REDIRECT_URI')
        if not self.provider:
            self.provider = app.config.get('PAUTH_PROVIDER', 'google')
        if not self.scopes:
            self.scopes = app.config.get('PAUTH_SCOPES')

    @property
    def client(self) -> OAuth2Client:
        """
        Get or create the OAuth2Client instance.

        Returns:
            OAuth2Client: OAuth client instance
        """
        if self._client is None:
            self._client = OAuth2Client(
                provider=self.provider,
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scopes=self.scopes,
                use_pkce=self.use_pkce
            )
        return self._client

    def authorize_redirect(
        self,
        scope: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Redirect to the OAuth provider's authorization page.

        Args:
            scope: OAuth scopes to request (overrides default)
            **kwargs: Additional parameters

        Returns:
            Flask redirect response
        """
        # Generate authorization URL
        auth_url = self.client.get_authorization_url(scope=scope, **kwargs)

        # Store state in session for validation
        if hasattr(self.client, '_state') and self.client._state:
            session['oauth_state'] = self.client._state

        # Store PKCE verifier in session if using PKCE
        if self.use_pkce and hasattr(self.client, '_code_verifier') and self.client._code_verifier:
            session['oauth_code_verifier'] = self.client._code_verifier

        return redirect(auth_url)

    def authorize_access_token(self) -> TokenResponse:
        """
        Handle the OAuth callback and exchange code for tokens.

        Returns:
            TokenResponse: OAuth tokens

        Raises:
            InvalidStateError: If state validation fails
            AuthorizationError: If authorization fails
        """
        # Get code and state from request
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')

        if error:
            raise AuthorizationError(f"Authorization failed: {error}")

        if not code:
            raise AuthorizationError("No authorization code received")

        # Validate state
        stored_state = session.get('oauth_state')
        if stored_state and state != stored_state:
            raise InvalidStateError("State parameter mismatch")

        # Restore PKCE verifier if using PKCE
        if self.use_pkce:
            code_verifier = session.get('oauth_code_verifier')
            if code_verifier:
                self.client._code_verifier = code_verifier

        # Exchange code for tokens
        tokens = self.client.exchange_code(code, state=state)

        # Clean up session
        session.pop('oauth_state', None)
        session.pop('oauth_code_verifier', None)

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

    def get_authorization_url(
        self,
        scope: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Get the authorization URL without redirecting.

        Args:
            scope: OAuth scopes to request
            **kwargs: Additional parameters

        Returns:
            str: Authorization URL
        """
        return self.client.get_authorization_url(scope=scope, **kwargs)
