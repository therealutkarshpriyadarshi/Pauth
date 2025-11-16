"""
Async OAuth Example

This example demonstrates using the async OAuth client with FastAPI.

Requirements:
- pip install fastapi
- pip install uvicorn
- pip install aiohttp

Usage:
    python async_example.py

Then visit: http://localhost:8000
"""

import asyncio

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, RedirectResponse
    import uvicorn
except ImportError:
    print("FastAPI and uvicorn are required for this example.")
    print("Install with: pip install fastapi uvicorn aiohttp")
    exit(1)

from src.async_client import AsyncOAuth2Client
from src.models import Providers

app = FastAPI(title="PAuth Async Example")

# Configure OAuth client
oauth_client = AsyncOAuth2Client(
    provider=Providers.GOOGLE,
    client_id="your_client_id",  # Replace with your client ID
    client_secret="your_client_secret",  # Replace with your client secret
    redirect_uri="http://localhost:8000/callback",
    scopes=["openid", "email", "profile"]
)

# In-memory session storage (use proper session management in production)
sessions = {}


@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page."""
    return """
    <html>
        <head><title>PAuth Async Example</title></head>
        <body>
            <h1>PAuth Async OAuth Example with FastAPI</h1>
            <p>This demonstrates async/await OAuth support</p>
            <a href="/login">
                <button style="padding: 10px 20px; font-size: 16px;">
                    Login with Google
                </button>
            </a>
        </body>
    </html>
    """


@app.get("/login")
async def login():
    """Initiate OAuth login."""
    # Generate authorization URL (this is still synchronous)
    auth_url = oauth_client.get_authorization_url()

    # Store state for validation (in production, use proper session management)
    sessions['current_state'] = oauth_client._state

    return RedirectResponse(auth_url)


@app.get("/callback")
async def callback(request: Request):
    """Handle OAuth callback."""
    # Get authorization code and state from query parameters
    code = request.query_params.get('code')
    state = request.query_params.get('state')

    if not code:
        return HTMLResponse("<h1>Error: No authorization code received</h1>", status_code=400)

    try:
        # Exchange code for tokens (ASYNC!)
        tokens = await oauth_client.exchange_code_async(code=code, state=state)

        # Get user information (ASYNC!)
        user_info = await oauth_client.get_user_info_async(tokens.access_token)

        # In production, save tokens and create user session here

        return HTMLResponse(f"""
        <html>
            <head><title>Login Success</title></head>
            <body>
                <h1>✅ Login Successful!</h1>
                <h2>User Information:</h2>
                <ul>
                    <li><strong>ID:</strong> {user_info.id}</li>
                    <li><strong>Email:</strong> {user_info.email}</li>
                    <li><strong>Name:</strong> {user_info.name}</li>
                </ul>
                <h3>Access Token (truncated):</h3>
                <code>{tokens.access_token[:50]}...</code>
                <br><br>
                <a href="/">Back to Home</a>
            </body>
        </html>
        """)

    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)


@app.get("/api/user")
async def get_user(access_token: str):
    """
    API endpoint to get user info (demonstrates async API usage).

    Usage: GET /api/user?access_token=YOUR_TOKEN
    """
    try:
        user_info = await oauth_client.get_user_info_async(access_token)
        return {
            "id": user_info.id,
            "email": user_info.email,
            "name": user_info.name,
            "picture": user_info.picture
        }
    except Exception as e:
        return {"error": str(e)}


def main():
    """Run the FastAPI application."""
    print("Starting FastAPI application with async OAuth support...")
    print("Visit http://localhost:8000 in your browser")
    print("\nMake sure to:")
    print("1. Replace 'your_client_id' and 'your_client_secret' with real credentials")
    print("2. Register http://localhost:8000/callback as a redirect URI\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
