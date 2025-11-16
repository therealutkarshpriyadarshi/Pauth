"""
Security auditor for OAuth 2.0 configurations.

This module provides automatic security scanning and recommendations
for OAuth 2.0 client configurations.
"""

from typing import List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

from src.client import OAuth2Client
from src.async_client import AsyncOAuth2Client
from src.storage import MemoryTokenStorage, FileTokenStorage


class Severity(Enum):
    """Security issue severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityIssue:
    """Represents a security issue found during audit."""
    severity: Severity
    title: str
    description: str
    recommendation: str
    category: str

    def __str__(self) -> str:
        """String representation with emoji indicators."""
        emoji_map = {
            Severity.INFO: "ℹ️ ",
            Severity.LOW: "⚪",
            Severity.MEDIUM: "🟡",
            Severity.HIGH: "🟠",
            Severity.CRITICAL: "🔴"
        }
        return f"{emoji_map[self.severity]} [{self.severity.value.upper()}] {self.title}"


@dataclass
class SecurityReport:
    """Security audit report."""
    client_info: Dict[str, Any]
    issues: List[SecurityIssue]
    score: int  # 0-100, higher is better
    passed_checks: int
    failed_checks: int
    total_checks: int

    @property
    def critical_issues(self) -> List[SecurityIssue]:
        """Get critical severity issues."""
        return [i for i in self.issues if i.severity == Severity.CRITICAL]

    @property
    def high_issues(self) -> List[SecurityIssue]:
        """Get high severity issues."""
        return [i for i in self.issues if i.severity == Severity.HIGH]

    @property
    def medium_issues(self) -> List[SecurityIssue]:
        """Get medium severity issues."""
        return [i for i in self.issues if i.severity == Severity.MEDIUM]

    @property
    def low_issues(self) -> List[SecurityIssue]:
        """Get low severity issues."""
        return [i for i in self.issues if i.severity == Severity.LOW]

    @property
    def has_critical_issues(self) -> bool:
        """Check if report has critical issues."""
        return len(self.critical_issues) > 0


class SecurityAuditor:
    """
    Security auditor for OAuth 2.0 configurations.

    Performs comprehensive security checks and provides recommendations
    for improving OAuth 2.0 security posture.

    Example:
        ```python
        from pauth.security import SecurityAuditor

        auditor = SecurityAuditor()
        report = auditor.audit(client)

        if report.has_critical_issues:
            print("CRITICAL ISSUES FOUND!")
            for issue in report.critical_issues:
                print(f"- {issue.title}")

        print(f"Security Score: {report.score}/100")
        ```
    """

    def __init__(self):
        """Initialize the security auditor."""
        self.issues: List[SecurityIssue] = []
        self.passed_checks = 0
        self.failed_checks = 0

    def audit(self, client: Union[OAuth2Client, AsyncOAuth2Client]) -> SecurityReport:
        """
        Perform comprehensive security audit.

        Args:
            client: OAuth2Client or AsyncOAuth2Client instance

        Returns:
            SecurityReport: Detailed security audit report
        """
        self.issues = []
        self.passed_checks = 0
        self.failed_checks = 0

        # Run all security checks
        self._check_pkce(client)
        self._check_redirect_uri(client)
        self._check_state_validation(client)
        self._check_token_storage(client)
        self._check_scopes(client)
        self._check_client_credentials(client)
        self._check_token_expiration(client)

        # Calculate security score
        total_checks = self.passed_checks + self.failed_checks
        score = self._calculate_score()

        # Gather client info
        client_info = {
            'provider': client.provider.__class__.__name__,
            'client_id': client.client_id[:10] + "..." if client.client_id else "Not set",
            'redirect_uri': client.redirect_uri,
            'scopes': client.scopes,
            'use_pkce': client.use_pkce
        }

        return SecurityReport(
            client_info=client_info,
            issues=self.issues,
            score=score,
            passed_checks=self.passed_checks,
            failed_checks=self.failed_checks,
            total_checks=total_checks
        )

    def _check_pkce(self, client: Union[OAuth2Client, AsyncOAuth2Client]):
        """Check PKCE configuration."""
        if not client.use_pkce:
            self.issues.append(SecurityIssue(
                severity=Severity.HIGH,
                title="PKCE Not Enabled",
                description="Proof Key for Code Exchange (PKCE) is not enabled. "
                           "PKCE provides additional security against authorization code interception attacks.",
                recommendation="Enable PKCE by setting use_pkce=True when initializing the client. "
                             "This is especially important for mobile and single-page applications.",
                category="Authentication Flow"
            ))
            self.failed_checks += 1
        else:
            self.passed_checks += 1

    def _check_redirect_uri(self, client: Union[OAuth2Client, AsyncOAuth2Client]):
        """Check redirect URI security."""
        if not client.redirect_uri:
            self.issues.append(SecurityIssue(
                severity=Severity.CRITICAL,
                title="No Redirect URI Configured",
                description="Redirect URI is not set. This is required for OAuth 2.0 flow.",
                recommendation="Set a valid redirect_uri when initializing the client.",
                category="Configuration"
            ))
            self.failed_checks += 1
            return

        parsed = urlparse(client.redirect_uri)

        # Check for HTTPS
        if parsed.scheme == 'http' and parsed.hostname not in ['localhost', '127.0.0.1']:
            self.issues.append(SecurityIssue(
                severity=Severity.CRITICAL,
                title="Insecure Redirect URI (HTTP)",
                description=f"Redirect URI uses HTTP instead of HTTPS: {client.redirect_uri}. "
                           "This exposes authorization codes to network eavesdropping.",
                recommendation="Use HTTPS for all redirect URIs in production. "
                             "HTTP is only acceptable for localhost development.",
                category="Transport Security"
            ))
            self.failed_checks += 1
        else:
            self.passed_checks += 1

        # Check for localhost in production
        if parsed.hostname in ['localhost', '127.0.0.1'] and parsed.scheme == 'http':
            self.issues.append(SecurityIssue(
                severity=Severity.INFO,
                title="Localhost Redirect URI Detected",
                description="Using localhost redirect URI. This is acceptable for development "
                           "but should not be used in production.",
                recommendation="Use a proper HTTPS redirect URI for production deployments.",
                category="Configuration"
            ))

    def _check_state_validation(self, client: Union[OAuth2Client, AsyncOAuth2Client]):
        """Check state parameter handling."""
        # State is automatically generated in the client, so we check if it's being used
        if hasattr(client, '_state') and client._state is None:
            self.issues.append(SecurityIssue(
                severity=Severity.MEDIUM,
                title="State Validation Not Active",
                description="State parameter is not currently set. State validation helps prevent CSRF attacks.",
                recommendation="Ensure you're validating the state parameter in your callback handler.",
                category="CSRF Protection"
            ))
            self.failed_checks += 1
        else:
            self.passed_checks += 1

    def _check_token_storage(self, client: Union[OAuth2Client, AsyncOAuth2Client]):
        """Check token storage security."""
        storage = client.token_storage

        if isinstance(storage, MemoryTokenStorage):
            self.issues.append(SecurityIssue(
                severity=Severity.MEDIUM,
                title="Tokens Stored in Memory",
                description="Tokens are stored in memory and will be lost on application restart. "
                           "This also doesn't protect tokens if memory is compromised.",
                recommendation="Consider using FileTokenStorage with encryption or a database-backed "
                             "storage solution for production applications.",
                category="Token Storage"
            ))
            self.failed_checks += 1

        elif isinstance(storage, FileTokenStorage):
            self.issues.append(SecurityIssue(
                severity=Severity.LOW,
                title="File-based Token Storage",
                description="Tokens are stored in files. While this provides persistence, "
                           "consider encryption for additional security.",
                recommendation="Use EncryptedFileStorage or database-backed storage for "
                             "production applications with sensitive data.",
                category="Token Storage"
            ))
            self.failed_checks += 1
        else:
            # Custom storage - assume it's properly configured
            self.passed_checks += 1

    def _check_scopes(self, client: Union[OAuth2Client, AsyncOAuth2Client]):
        """Check OAuth scopes."""
        if not client.scopes or len(client.scopes) == 0:
            self.issues.append(SecurityIssue(
                severity=Severity.LOW,
                title="No Scopes Specified",
                description="No OAuth scopes are configured. The provider may grant default scopes "
                           "which might be broader than necessary.",
                recommendation="Explicitly specify the minimum required scopes following the "
                             "principle of least privilege.",
                category="Authorization"
            ))
            self.failed_checks += 1
        else:
            # Check for overly broad scopes
            broad_scopes = ['admin', 'write:all', 'delete:all', 'full_access']
            found_broad = [s for s in client.scopes if any(b in s.lower() for b in broad_scopes)]

            if found_broad:
                self.issues.append(SecurityIssue(
                    severity=Severity.MEDIUM,
                    title="Overly Broad Scopes Requested",
                    description=f"Requesting potentially broad scopes: {', '.join(found_broad)}",
                    recommendation="Request only the minimum scopes necessary for your application. "
                                 "Avoid admin or write:all type scopes unless absolutely required.",
                    category="Authorization"
                ))
                self.failed_checks += 1
            else:
                self.passed_checks += 1

    def _check_client_credentials(self, client: Union[OAuth2Client, AsyncOAuth2Client]):
        """Check client credentials handling."""
        if not client.client_id:
            self.issues.append(SecurityIssue(
                severity=Severity.CRITICAL,
                title="No Client ID",
                description="Client ID is not set.",
                recommendation="Configure client_id from your OAuth provider.",
                category="Configuration"
            ))
            self.failed_checks += 1
            return
        else:
            self.passed_checks += 1

        if not client.use_pkce and not client.client_secret:
            self.issues.append(SecurityIssue(
                severity=Severity.CRITICAL,
                title="No Client Secret and PKCE Disabled",
                description="Client secret is not set and PKCE is disabled. "
                           "At least one authentication method is required.",
                recommendation="Either set client_secret or enable PKCE (use_pkce=True).",
                category="Configuration"
            ))
            self.failed_checks += 1
        else:
            self.passed_checks += 1

    def _check_token_expiration(self, client: Union[OAuth2Client, AsyncOAuth2Client]):
        """Check token expiration handling."""
        # This is more of a general recommendation
        self.issues.append(SecurityIssue(
            severity=Severity.INFO,
            title="Token Expiration Monitoring",
            description="Ensure your application properly handles token expiration and refresh.",
            recommendation="Implement automatic token refresh before expiration and handle "
                         "token expiration errors gracefully.",
            category="Token Management"
        ))

    def _calculate_score(self) -> int:
        """
        Calculate security score (0-100).

        Score calculation:
        - Start with 100
        - Deduct points based on severity:
          - Critical: -30 points each
          - High: -20 points each
          - Medium: -10 points each
          - Low: -5 points each
          - Info: -0 points

        Returns:
            int: Security score (0-100)
        """
        score = 100

        for issue in self.issues:
            if issue.severity == Severity.CRITICAL:
                score -= 30
            elif issue.severity == Severity.HIGH:
                score -= 20
            elif issue.severity == Severity.MEDIUM:
                score -= 10
            elif issue.severity == Severity.LOW:
                score -= 5

        return max(0, score)  # Ensure score doesn't go below 0
