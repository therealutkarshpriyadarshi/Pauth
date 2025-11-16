# PAuth Examples

This directory contains example applications demonstrating how to use PAuth for OAuth 2.0 authentication.

## Examples

### 1. Basic Example (`basic_example.py`)

A simple command-line example demonstrating the core OAuth 2.0 flow:
- Generating authorization URLs
- Exchanging codes for tokens
- Fetching user information

**Usage:**
```bash
python basic_example.py
```

### 2. Flask Example (`flask_example.py`)

A complete Flask web application with OAuth 2.0 login.

**Setup:**
```bash
pip install Flask
python flask_example.py
```

Then visit `http://localhost:5000` in your browser.

## Configuration

Before running the examples, you need to:

1. **Register your application** with the OAuth provider (Google, GitHub, etc.)
2. **Get your credentials** (client_id and client_secret)
3. **Update the configuration** in each example file

### Getting OAuth Credentials

**Google:**
- Visit [Google Cloud Console](https://console.cloud.google.com/)
- Create a new project or select existing
- Enable Google+ API
- Create OAuth 2.0 credentials
- Add redirect URIs

**GitHub:**
- Visit [GitHub Developer Settings](https://github.com/settings/developers)
- Create a new OAuth App
- Note your Client ID and Client Secret

**Facebook:**
- Visit [Facebook Developers](https://developers.facebook.com/)
- Create a new app
- Add Facebook Login product
- Get your App ID and App Secret

## Security Notes

- Never commit credentials to version control
- Use environment variables for sensitive data in production
- Use HTTPS for redirect URIs in production
- Keep your secret keys secret!
