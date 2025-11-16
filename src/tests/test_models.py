"""
Tests for PAuth models.
"""

import unittest
from datetime import datetime, timedelta

from src.models import TokenResponse, UserInfo, Providers


class TestTokenResponse(unittest.TestCase):
    """Test cases for TokenResponse model."""

    def test_token_response_creation(self):
        """Test creating a TokenResponse."""
        tokens = TokenResponse(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600
        )

        self.assertEqual(tokens.access_token, "test_token")
        self.assertEqual(tokens.token_type, "Bearer")
        self.assertEqual(tokens.expires_in, 3600)

    def test_token_expiration_calculation(self):
        """Test token expiration time calculation."""
        tokens = TokenResponse(
            access_token="test_token",
            expires_in=3600
        )

        expires_at = tokens.expires_at
        self.assertIsNotNone(expires_at)

        # Should expire roughly 1 hour from now
        expected = datetime.utcnow() + timedelta(seconds=3600)
        delta = abs((expires_at - expected).total_seconds())
        self.assertLess(delta, 2)  # Within 2 seconds

    def test_is_expired(self):
        """Test checking if token is expired."""
        # Token that expires in the future
        future_tokens = TokenResponse(
            access_token="test_token",
            expires_in=3600
        )
        self.assertFalse(future_tokens.is_expired)

        # Token with no expiration
        no_expiry_tokens = TokenResponse(
            access_token="test_token"
        )
        self.assertFalse(no_expiry_tokens.is_expired)

    def test_scopes_property(self):
        """Test scopes property."""
        tokens = TokenResponse(
            access_token="test_token",
            scope="openid email profile"
        )

        scopes = tokens.scopes
        self.assertEqual(len(scopes), 3)
        self.assertIn("openid", scopes)
        self.assertIn("email", scopes)
        self.assertIn("profile", scopes)

    def test_to_dict(self):
        """Test converting token to dictionary."""
        tokens = TokenResponse(
            access_token="test_token",
            token_type="Bearer",
            expires_in=3600
        )

        token_dict = tokens.to_dict()
        self.assertEqual(token_dict['access_token'], "test_token")
        self.assertEqual(token_dict['token_type'], "Bearer")

    def test_from_dict(self):
        """Test creating token from dictionary."""
        data = {
            'access_token': 'test_token',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': 'refresh_token'
        }

        tokens = TokenResponse.from_dict(data)
        self.assertEqual(tokens.access_token, 'test_token')
        self.assertEqual(tokens.refresh_token, 'refresh_token')


class TestUserInfo(unittest.TestCase):
    """Test cases for UserInfo model."""

    def test_user_info_creation(self):
        """Test creating a UserInfo object."""
        user = UserInfo(
            id="123",
            email="test@example.com",
            name="Test User"
        )

        self.assertEqual(user.id, "123")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "Test User")

    def test_from_dict(self):
        """Test creating UserInfo from dictionary."""
        data = {
            'id': '123',
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': 'https://example.com/pic.jpg'
        }

        user = UserInfo.from_dict(data)
        self.assertEqual(user.id, '123')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.picture, 'https://example.com/pic.jpg')

    def test_from_dict_with_sub(self):
        """Test creating UserInfo from dict with 'sub' field."""
        data = {
            'sub': '123',
            'email': 'test@example.com'
        }

        user = UserInfo.from_dict(data)
        self.assertEqual(user.id, '123')


class TestProviders(unittest.TestCase):
    """Test cases for Providers enum."""

    def test_provider_values(self):
        """Test provider enum values."""
        self.assertEqual(Providers.GOOGLE.value, "google")
        self.assertEqual(Providers.GITHUB.value, "github")
        self.assertEqual(Providers.FACEBOOK.value, "facebook")

    def test_from_string(self):
        """Test getting provider from string."""
        provider = Providers.from_string("google")
        self.assertEqual(provider, Providers.GOOGLE)

        provider = Providers.from_string("GITHUB")
        self.assertEqual(provider, Providers.GITHUB)

    def test_from_string_invalid(self):
        """Test getting provider with invalid string."""
        with self.assertRaises(ValueError):
            Providers.from_string("invalid_provider")

    def test_display_name(self):
        """Test provider display names."""
        self.assertEqual(Providers.GOOGLE.display_name, "Google")
        self.assertEqual(Providers.GITHUB.display_name, "GitHub")

    def test_get_provider_class(self):
        """Test getting provider class."""
        provider_class = Providers.GOOGLE.get_provider_class()
        self.assertIsNotNone(provider_class)


if __name__ == '__main__':
    unittest.main()
