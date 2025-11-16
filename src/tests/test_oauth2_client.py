"""
Tests for OAuth2Client.
"""

import unittest
from unittest.mock import Mock, patch

from src.client import OAuth2Client
from src.models import Providers
from src.exceptions import ConfigurationError


class TestOAuth2Client(unittest.TestCase):
    """Test cases for OAuth2Client."""

    def setUp(self):
        """Set up test fixtures."""
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"
        self.redirect_uri = "http://localhost:8000/callback"

    def test_initialization_with_provider_enum(self):
        """Test client initialization with Providers enum."""
        client = OAuth2Client(
            provider=Providers.GOOGLE,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri
        )
        self.assertIsNotNone(client)
        self.assertEqual(client.client_id, self.client_id)
        self.assertEqual(client.client_secret, self.client_secret)

    def test_initialization_with_provider_string(self):
        """Test client initialization with provider string."""
        client = OAuth2Client(
            provider="google",
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri
        )
        self.assertIsNotNone(client)

    def test_initialization_without_client_id_raises_error(self):
        """Test that missing client_id raises ConfigurationError."""
        with self.assertRaises(ConfigurationError):
            OAuth2Client(
                provider=Providers.GOOGLE,
                client_id=None,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri
            )

    def test_get_authorization_url(self):
        """Test generating authorization URL."""
        client = OAuth2Client(
            provider=Providers.GOOGLE,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri
        )

        auth_url = client.get_authorization_url(
            scope=["openid", "email"]
        )

        self.assertIn("https://accounts.google.com", auth_url)
        self.assertIn("client_id=", auth_url)
        self.assertIn("redirect_uri=", auth_url)
        self.assertIn("scope=", auth_url)

    def test_generate_state(self):
        """Test state generation."""
        state1 = OAuth2Client.generate_state()
        state2 = OAuth2Client.generate_state()

        self.assertIsNotNone(state1)
        self.assertIsNotNone(state2)
        self.assertNotEqual(state1, state2)
        self.assertGreater(len(state1), 20)

    def test_pkce_code_verifier_generation(self):
        """Test PKCE code verifier generation."""
        verifier = OAuth2Client._generate_code_verifier()

        self.assertIsNotNone(verifier)
        self.assertGreater(len(verifier), 40)

    def test_pkce_code_challenge_generation(self):
        """Test PKCE code challenge generation."""
        verifier = "test_verifier"
        challenge = OAuth2Client._generate_code_challenge(verifier)

        self.assertIsNotNone(challenge)
        self.assertGreater(len(challenge), 20)


if __name__ == '__main__':
    unittest.main()
