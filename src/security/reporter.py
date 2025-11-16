"""
Security report formatting and display.
"""

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich import box
except ImportError:
    Console = None

from .auditor import SecurityReport, Severity


class SecurityReporter:
    """
    Formats and displays security audit reports.

    Example:
        ```python
        from pauth.security import SecurityAuditor, SecurityReporter

        auditor = SecurityAuditor()
        report = auditor.audit(client)

        reporter = SecurityReporter()
        reporter.print_report(report)
        ```
    """

    def __init__(self, use_color: bool = True):
        """
        Initialize the security reporter.

        Args:
            use_color: Whether to use colored output (requires Rich library)
        """
        self.use_color = use_color and Console is not None
        self.console = Console() if self.use_color else None

    def print_report(self, report: SecurityReport):
        """
        Print a formatted security report.

        Args:
            report: SecurityReport to display
        """
        if self.use_color and self.console:
            self._print_rich_report(report)
        else:
            self._print_plain_report(report)

    def _print_rich_report(self, report: SecurityReport):
        """Print report with Rich formatting."""
        console = self.console

        # Header
        console.print("\n")
        console.print("╔════════════════════════════════════════════════════════╗", style="bold cyan")
        console.print("║    🛡️  OAuth 2.0 Security Audit Report               ║", style="bold cyan")
        console.print("╚════════════════════════════════════════════════════════╝", style="bold cyan")
        console.print()

        # Score panel
        score_color = self._get_score_color(report.score)
        score_panel = Panel(
            f"[bold {score_color}]{report.score}/100[/]\n\n"
            f"Passed Checks: [green]{report.passed_checks}[/]\n"
            f"Failed Checks: [red]{report.failed_checks}[/]\n"
            f"Total Checks: {report.total_checks}",
            title="🎯 Security Score",
            border_style=score_color,
            width=60
        )
        console.print(score_panel)
        console.print()

        # Client info
        info_table = Table(title="📋 Client Configuration", box=box.ROUNDED, show_header=False)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="yellow")

        for key, value in report.client_info.items():
            info_table.add_row(key.replace('_', ' ').title(), str(value))

        console.print(info_table)
        console.print()

        # Issues by severity
        if report.critical_issues:
            console.print(f"\n🔴 [bold red]CRITICAL Issues ({len(report.critical_issues)}):[/]")
            for issue in report.critical_issues:
                self._print_issue(issue)

        if report.high_issues:
            console.print(f"\n🟠 [bold orange]HIGH Severity Issues ({len(report.high_issues)}):[/]")
            for issue in report.high_issues:
                self._print_issue(issue)

        if report.medium_issues:
            console.print(f"\n🟡 [bold yellow]MEDIUM Severity Issues ({len(report.medium_issues)}):[/]")
            for issue in report.medium_issues:
                self._print_issue(issue)

        if report.low_issues:
            console.print(f"\n⚪ [bold white]LOW Severity Issues ({len(report.low_issues)}):[/]")
            for issue in report.low_issues:
                self._print_issue(issue)

        # Summary
        console.print()
        if report.has_critical_issues:
            console.print(
                Panel(
                    "[bold red]⚠️  CRITICAL ISSUES DETECTED![/]\n\n"
                    "Your OAuth configuration has critical security issues that must be addressed immediately.\n"
                    "Review the recommendations above and fix all critical issues before deploying to production.",
                    border_style="red",
                    title="❌ Security Alert"
                )
            )
        elif report.score >= 80:
            console.print(
                Panel(
                    "[bold green]✅ Good security posture![/]\n\n"
                    "Your OAuth configuration follows most security best practices.\n"
                    "Review the recommendations to further improve security.",
                    border_style="green",
                    title="✓ Security Status"
                )
            )
        else:
            console.print(
                Panel(
                    "[bold yellow]⚠️  Security improvements recommended[/]\n\n"
                    "Your OAuth configuration has some security issues.\n"
                    "Review and address the recommendations above.",
                    border_style="yellow",
                    title="⚠️ Security Status"
                )
            )

        console.print()

    def _print_issue(self, issue):
        """Print a single issue with Rich formatting."""
        severity_colors = {
            Severity.CRITICAL: "red",
            Severity.HIGH: "orange3",
            Severity.MEDIUM: "yellow",
            Severity.LOW: "white",
            Severity.INFO: "cyan"
        }

        color = severity_colors.get(issue.severity, "white")

        issue_panel = Panel(
            f"[bold]{issue.title}[/]\n\n"
            f"[italic]{issue.description}[/]\n\n"
            f"[bold green]💡 Recommendation:[/] {issue.recommendation}\n\n"
            f"[dim]Category: {issue.category}[/]",
            border_style=color,
            width=80
        )

        self.console.print(issue_panel)
        self.console.print()

    def _print_plain_report(self, report: SecurityReport):
        """Print report in plain text (no colors)."""
        print("\n" + "=" * 60)
        print("OAuth 2.0 Security Audit Report")
        print("=" * 60)

        print(f"\nSecurity Score: {report.score}/100")
        print(f"Passed Checks: {report.passed_checks}")
        print(f"Failed Checks: {report.failed_checks}")
        print(f"Total Checks: {report.total_checks}")

        print("\nClient Configuration:")
        for key, value in report.client_info.items():
            print(f"  {key}: {value}")

        print("\nIssues Found:")

        if report.critical_issues:
            print(f"\nCRITICAL Issues ({len(report.critical_issues)}):")
            for issue in report.critical_issues:
                self._print_plain_issue(issue)

        if report.high_issues:
            print(f"\nHIGH Severity Issues ({len(report.high_issues)}):")
            for issue in report.high_issues:
                self._print_plain_issue(issue)

        if report.medium_issues:
            print(f"\nMEDIUM Severity Issues ({len(report.medium_issues)}):")
            for issue in report.medium_issues:
                self._print_plain_issue(issue)

        if report.low_issues:
            print(f"\nLOW Severity Issues ({len(report.low_issues)}):")
            for issue in report.low_issues:
                self._print_plain_issue(issue)

        print("\n" + "=" * 60)

    def _print_plain_issue(self, issue):
        """Print a single issue in plain text."""
        print(f"\n  [{issue.severity.value.upper()}] {issue.title}")
        print(f"  Description: {issue.description}")
        print(f"  Recommendation: {issue.recommendation}")
        print(f"  Category: {issue.category}")

    def _get_score_color(self, score: int) -> str:
        """Get color based on score."""
        if score >= 80:
            return "green"
        elif score >= 60:
            return "yellow"
        elif score >= 40:
            return "orange3"
        else:
            return "red"
