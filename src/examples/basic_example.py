"""
Basic OAuth 2.0 example using PAuth.

This example demonstrates the basic OAuth 2.0 flow:
1. Generate authorization URL
2. User authorizes (simulated)
3. Exchange code for tokens
4. Fetch user information
"""

from src.client import OAuth2Client
from src.models import Providers

# Configuration
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "http://localhost:8000/callback"


def main():
    """
    Demonstrate basic OAuth 2.0 flow.
    """
    # Initialize OAuth2 client with Google provider
    client = OAuth2Client(
        provider=Providers.GOOGLE,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI
    )

    # Step 1: Get authorization URL
    print("Step 1: Getting authorization URL...")
    auth_url = client.get_authorization_url(
        scope=["openid", "email", "profile"]
    )
    print(f"Authorization URL: {auth_url}\n")
    print("User would visit this URL to authorize the application.\n")

    # Step 2: User authorizes (simulated)
    # In a real application, the user would be redirected to auth_url
    # and then back to your redirect_uri with a code parameter
    print("Step 2: User authorizes and is redirected back with a code")
    code = input("Enter the authorization code from the callback: ")
    state = input("Enter the state parameter from the callback: ")

    # Step 3: Exchange code for tokens
    print("\nStep 3: Exchanging code for tokens...")
    try:
        tokens = client.exchange_code(code=code, state=state)
        print(f"Access Token: {tokens.access_token[:20]}...")
        print(f"Token Type: {tokens.token_type}")
        print(f"Expires In: {tokens.expires_in} seconds")
        if tokens.refresh_token:
            print(f"Refresh Token: {tokens.refresh_token[:20]}...")

        # Step 4: Fetch user information
        print("\nStep 4: Fetching user information...")
        user_info = client.get_user_info(tokens.access_token)
        print(f"User ID: {user_info.id}")
        print(f"Email: {user_info.email}")
        print(f"Name: {user_info.name}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
