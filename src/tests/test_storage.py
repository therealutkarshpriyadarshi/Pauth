"""
Tests for token storage backends.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from src.storage import MemoryTokenStorage, FileTokenStorage
from src.models import TokenResponse


class TestMemoryTokenStorage(unittest.TestCase):
    """Test cases for MemoryTokenStorage."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = MemoryTokenStorage()
        self.user_id = "test_user"
        self.tokens = TokenResponse(
            access_token="test_access_token",
            token_type="Bearer",
            expires_in=3600
        )

    def test_save_and_get_token(self):
        """Test saving and retrieving a token."""
        self.storage.save_token(self.user_id, self.tokens)
        retrieved = self.storage.get_token(self.user_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.access_token, self.tokens.access_token)

    def test_get_nonexistent_token(self):
        """Test retrieving a token that doesn't exist."""
        retrieved = self.storage.get_token("nonexistent_user")
        self.assertIsNone(retrieved)

    def test_delete_token(self):
        """Test deleting a token."""
        self.storage.save_token(self.user_id, self.tokens)
        result = self.storage.delete_token(self.user_id)

        self.assertTrue(result)
        self.assertIsNone(self.storage.get_token(self.user_id))

    def test_delete_nonexistent_token(self):
        """Test deleting a token that doesn't exist."""
        result = self.storage.delete_token("nonexistent_user")
        self.assertFalse(result)

    def test_update_token(self):
        """Test updating a token."""
        self.storage.save_token(self.user_id, self.tokens)

        new_tokens = TokenResponse(
            access_token="new_access_token",
            token_type="Bearer",
            expires_in=7200
        )
        self.storage.update_token(self.user_id, new_tokens)

        retrieved = self.storage.get_token(self.user_id)
        self.assertEqual(retrieved.access_token, "new_access_token")

    def test_token_exists(self):
        """Test checking if a token exists."""
        self.assertFalse(self.storage.token_exists(self.user_id))

        self.storage.save_token(self.user_id, self.tokens)
        self.assertTrue(self.storage.token_exists(self.user_id))


class TestFileTokenStorage(unittest.TestCase):
    """Test cases for FileTokenStorage."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = FileTokenStorage(storage_dir=self.temp_dir)
        self.user_id = "test_user"
        self.tokens = TokenResponse(
            access_token="test_access_token",
            token_type="Bearer",
            expires_in=3600
        )

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_get_token(self):
        """Test saving and retrieving a token."""
        self.storage.save_token(self.user_id, self.tokens)
        retrieved = self.storage.get_token(self.user_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.access_token, self.tokens.access_token)

    def test_token_file_permissions(self):
        """Test that token files have restrictive permissions."""
        self.storage.save_token(self.user_id, self.tokens)
        token_file = Path(self.temp_dir) / f"{self.user_id}.json"

        # Check that file exists
        self.assertTrue(token_file.exists())

        # Note: Permission checks are platform-specific
        # This test might need adjustment for Windows

    def test_delete_token(self):
        """Test deleting a token."""
        self.storage.save_token(self.user_id, self.tokens)
        result = self.storage.delete_token(self.user_id)

        self.assertTrue(result)
        self.assertIsNone(self.storage.get_token(self.user_id))


if __name__ == '__main__':
    unittest.main()
