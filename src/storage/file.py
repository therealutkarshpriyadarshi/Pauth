"""
File-based token storage implementation.
"""

import json
import os
from pathlib import Path
from typing import Optional

from src.exceptions import TokenStorageError
from src.models.tokens import TokenResponse
from src.storage.base import BaseTokenStorage


class FileTokenStorage(BaseTokenStorage):
    """
    File-based token storage.

    This storage backend saves tokens as JSON files in a directory.
    Suitable for:
    - Single-user applications
    - Development and testing
    - Persistent storage without a database

    Note: Not recommended for production multi-user applications.
    """

    def __init__(self, storage_dir: str = ".pauth_tokens"):
        """
        Initialize file-based storage.

        Args:
            storage_dir (str): Directory to store token files
        """
        self.storage_dir = Path(storage_dir)
        self._ensure_storage_dir()

    def _ensure_storage_dir(self) -> None:
        """Create storage directory if it doesn't exist."""
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            # Set restrictive permissions (owner only)
            os.chmod(self.storage_dir, 0o700)
        except Exception as e:
            raise TokenStorageError(f"Failed to create storage directory: {e}")

    def _get_token_path(self, user_id: str) -> Path:
        """
        Get the file path for a user's tokens.

        Args:
            user_id (str): User identifier

        Returns:
            Path: Path to the token file
        """
        # Sanitize user_id to prevent directory traversal
        safe_user_id = "".join(c for c in user_id if c.isalnum() or c in ('_', '-'))
        return self.storage_dir / f"{safe_user_id}.json"

    def save_token(self, user_id: str, tokens: TokenResponse) -> None:
        """
        Save tokens for a user to a file.

        Args:
            user_id (str): Unique identifier for the user
            tokens (TokenResponse): Token response to save

        Raises:
            TokenStorageError: If saving fails
        """
        try:
            token_path = self._get_token_path(user_id)
            token_data = tokens.to_dict()

            with open(token_path, 'w') as f:
                json.dump(token_data, f, indent=2)

            # Set restrictive permissions (owner only)
            os.chmod(token_path, 0o600)

        except Exception as e:
            raise TokenStorageError(f"Failed to save token for user {user_id}: {e}")

    def get_token(self, user_id: str) -> Optional[TokenResponse]:
        """
        Retrieve tokens for a user from file.

        Args:
            user_id (str): Unique identifier for the user

        Returns:
            TokenResponse: Stored tokens, or None if not found

        Raises:
            TokenStorageError: If retrieval fails
        """
        try:
            token_path = self._get_token_path(user_id)

            if not token_path.exists():
                return None

            with open(token_path, 'r') as f:
                token_data = json.load(f)

            return TokenResponse.from_dict(token_data)

        except json.JSONDecodeError as e:
            raise TokenStorageError(f"Corrupted token file for user {user_id}: {e}")
        except Exception as e:
            raise TokenStorageError(f"Failed to retrieve token for user {user_id}: {e}")

    def delete_token(self, user_id: str) -> bool:
        """
        Delete tokens for a user.

        Args:
            user_id (str): Unique identifier for the user

        Returns:
            bool: True if deleted, False if not found

        Raises:
            TokenStorageError: If deletion fails
        """
        try:
            token_path = self._get_token_path(user_id)

            if not token_path.exists():
                return False

            token_path.unlink()
            return True

        except Exception as e:
            raise TokenStorageError(f"Failed to delete token for user {user_id}: {e}")

    def update_token(self, user_id: str, tokens: TokenResponse) -> None:
        """
        Update tokens for a user.

        Args:
            user_id (str): Unique identifier for the user
            tokens (TokenResponse): New token response

        Raises:
            TokenStorageError: If update fails
        """
        self.save_token(user_id, tokens)

    def clear_all(self) -> None:
        """
        Clear all stored tokens.

        Raises:
            TokenStorageError: If clearing fails
        """
        try:
            for token_file in self.storage_dir.glob("*.json"):
                token_file.unlink()
        except Exception as e:
            raise TokenStorageError(f"Failed to clear tokens: {e}")
