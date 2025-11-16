"""
Flask OAuth 2.0 example using PAuth.

This example demonstrates how to integrate OAuth 2.0 into a Flask application.

To run this example:
1. Install Flask: pip install Flask
2. Set your OAuth credentials in the config
3. Run: python flask_example.py
4. Visit: http://localhost:5000
"""

try:
    from flask import Flask, redirect, url_for, session
    from src.integrations.flask import FlaskOAuth
except ImportError:
    print("Flask is not installed. Install it with: pip install Flask")
    exit(1)

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configure OAuth
app.config['PAUTH_PROVIDER'] = 'google'
app.config['PAUTH_CLIENT_ID'] = 'your_client_id'
app.config['PAUTH_CLIENT_SECRET'] = 'your_client_secret'
app.config['PAUTH_REDIRECT_URI'] = 'http://localhost:5000/callback'
app.config['PAUTH_SCOPES'] = ['openid', 'email', 'profile']

# Initialize OAuth
oauth = FlaskOAuth(app=app)


@app.route('/')
def index():
    """Home page."""
    user = session.get('user')
    if user:
        return f"""
        <h1>Welcome, {user['name']}!</h1>
        <p>Email: {user['email']}</p>
        <a href="/logout">Logout</a>
        """
    else:
        return '''
        <h1>PAuth Flask Example</h1>
        <a href="/login">Login with Google</a>
        '''


@app.route('/login')
def login():
    """Initiate OAuth login."""
    return oauth.authorize_redirect()


@app.route('/callback')
def callback():
    """Handle OAuth callback."""
    try:
        # Get tokens
        tokens = oauth.authorize_access_token()

        # Get user info
        user_info = oauth.get_user_info(tokens.access_token)

        # Store in session
        session['user'] = {
            'id': user_info.id,
            'email': user_info.email,
            'name': user_info.name,
        }
        session['tokens'] = {
            'access_token': tokens.access_token,
            'refresh_token': tokens.refresh_token,
        }

        return redirect(url_for('index'))

    except Exception as e:
        return f"Error: {e}", 400


@app.route('/logout')
def logout():
    """Logout user."""
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("Starting Flask application...")
    print("Visit http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
