"""
Security Scanner Example

This example demonstrates using the security auditor to scan
OAuth configurations for security issues.

Requirements:
- pip install rich (for colorful output)

Usage:
    python security_scanner_example.py
"""

from src.client import OAuth2Client
from src.models import Providers
from src.security import SecurityAuditor, SecurityReporter


def scan_secure_config():
    """Example of a secure OAuth configuration."""
    print("\n" + "=" * 60)
    print("Scanning SECURE Configuration")
    print("=" * 60)

    client = OAuth2Client(
        provider=Providers.GOOGLE,
        client_id="demo_client_id_12345",
        client_secret="demo_secret",
        redirect_uri="https://myapp.com/callback",  # HTTPS!
        scopes=["openid", "email"],  # Minimal scopes
        use_pkce=True  # PKCE enabled
    )

    # Run security audit
    auditor = SecurityAuditor()
    report = auditor.audit(client)

    # Display report
    reporter = SecurityReporter()
    reporter.print_report(report)


def scan_insecure_config():
    """Example of an insecure OAuth configuration."""
    print("\n" + "=" * 60)
    print("Scanning INSECURE Configuration (for demonstration)")
    print("=" * 60)

    client = OAuth2Client(
        provider=Providers.GITHUB,
        client_id="demo_client",
        client_secret="demo_secret",
        redirect_uri="http://myapp.com/callback",  # HTTP - not secure!
        scopes=[],  # No scopes specified
        use_pkce=False  # PKCE not enabled
    )

    # Run security audit
    auditor = SecurityAuditor()
    report = auditor.audit(client)

    # Display report
    reporter = SecurityReporter()
    reporter.print_report(report)

    # Check for critical issues
    if report.has_critical_issues:
        print("\n⚠️  CRITICAL SECURITY ISSUES FOUND!")
        print("This configuration should NOT be used in production.\n")

        print("Critical issues:")
        for issue in report.critical_issues:
            print(f"  - {issue.title}")


def scan_localhost_config():
    """Example of a localhost development configuration."""
    print("\n" + "=" * 60)
    print("Scanning LOCALHOST Development Configuration")
    print("=" * 60)

    client = OAuth2Client(
        provider=Providers.GOOGLE,
        client_id="dev_client_id",
        client_secret="dev_secret",
        redirect_uri="http://localhost:8000/callback",  # Localhost is OK for dev
        scopes=["openid", "email", "profile"],
        use_pkce=True
    )

    auditor = SecurityAuditor()
    report = auditor.audit(client)

    reporter = SecurityReporter()
    reporter.print_report(report)


def main():
    """Run security scanner examples."""
    print("╔════════════════════════════════════════════════════════╗")
    print("║   PAuth Security Scanner - Examples                   ║")
    print("╚════════════════════════════════════════════════════════╝")

    # Scan different configurations
    scan_secure_config()
    scan_insecure_config()
    scan_localhost_config()

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
The security scanner helps you identify potential security issues
in your OAuth configuration before deployment.

Key recommendations:
✓ Always use HTTPS for redirect URIs in production
✓ Enable PKCE for additional security
✓ Request only necessary OAuth scopes
✓ Use secure token storage
✓ Validate state parameters

Run the scanner on your own configuration with:

    from pauth.security import SecurityAuditor, SecurityReporter

    auditor = SecurityAuditor()
    report = auditor.audit(your_client)

    reporter = SecurityReporter()
    reporter.print_report(report)
    """)


if __name__ == "__main__":
    main()
