"""
OAuth Playground Example

This example demonstrates how to use the interactive OAuth playground
for testing OAuth flows with beautiful terminal UI.

Requirements:
- pip install rich
- pip install qrcode (optional, for QR code support)

Usage:
    python playground_example.py
"""

from src.playground import OAuthPlayground


def main():
    """Run the OAuth playground."""
    print("Starting PAuth OAuth Playground...")
    print("This interactive tool will guide you through testing OAuth flows.\n")

    playground = OAuthPlayground()
    playground.test_flow()


if __name__ == "__main__":
    main()
