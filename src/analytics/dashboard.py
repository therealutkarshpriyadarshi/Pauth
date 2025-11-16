"""
Analytics dashboard visualization.
"""

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.bar import Bar
    from rich import box
    from rich.progress import Progress, BarColumn, TextColumn
except ImportError:
    Console = None

from .tracker import OAuthAnalytics, AnalyticsReport


class AnalyticsDashboard:
    """
    Interactive analytics dashboard with visualizations.

    Example:
        ```python
        from pauth.analytics import OAuthAnalytics, AnalyticsDashboard

        analytics = OAuthAnalytics()
        # ... track events ...

        dashboard = AnalyticsDashboard(analytics)
        dashboard.show()  # Display interactive dashboard
        dashboard.show_provider_breakdown()  # Show provider stats
        ```
    """

    def __init__(self, analytics: OAuthAnalytics):
        """
        Initialize the dashboard.

        Args:
            analytics: OAuthAnalytics instance
        """
        self.analytics = analytics
        self.console = Console() if Console else None

    def show(self, period: str = 'last_24_hours'):
        """
        Display the complete dashboard.

        Args:
            period: Time period for the report
        """
        if not self.console:
            print("Rich library required for dashboard. Install with: pip install rich")
            return

        report = self.analytics.generate_report(period=period)

        self.console.clear()
        self.console.print()
        self._show_header(period)
        self._show_overview(report)
        self._show_provider_breakdown(report)
        self._show_hourly_distribution(report)
        self._show_failure_analysis(report)
        self.console.print()

    def _show_header(self, period: str):
        """Display dashboard header."""
        header = f"""
        [bold cyan]╔═══════════════════════════════════════════════════════╗[/]
        [bold cyan]║[/]    [bold magenta]📊 OAuth Analytics Dashboard[/]                  [bold cyan]║[/]
        [bold cyan]╚═══════════════════════════════════════════════════════╝[/]

        [yellow]Period: {period.replace('_', ' ').title()}[/]
        """

        self.console.print(Panel(header, border_style="cyan"))

    def _show_overview(self, report: AnalyticsReport):
        """Display overview metrics."""
        self.console.print("\n[bold cyan]📈 Overview[/]\n")

        # Create metrics table
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="green", justify="right")

        table.add_row("Total Events", str(report.total_events))
        table.add_row("Login Attempts", str(report.login_attempts))
        table.add_row("Successful Logins", str(report.login_successes))
        table.add_row("Failed Logins", str(report.login_failures))

        # Success rate with color
        success_color = self._get_rate_color(report.success_rate)
        table.add_row(
            "Success Rate",
            f"[{success_color}]{report.success_rate}%[/]"
        )

        if report.avg_duration_ms > 0:
            table.add_row(
                "Avg Response Time",
                f"{report.avg_duration_ms:.0f}ms"
            )

        self.console.print(table)

        # Success rate progress bar
        self.console.print()
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[bold green]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task(
                "Success Rate",
                total=100,
                completed=report.success_rate
            )

    def _show_provider_breakdown(self, report: AnalyticsReport):
        """Display provider-specific statistics."""
        self.console.print("\n[bold cyan]🌐 Provider Breakdown[/]\n")

        if not report.provider_stats:
            self.console.print("[yellow]No provider data available[/]")
            return

        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Provider", style="cyan")
        table.add_column("Total", justify="right", style="blue")
        table.add_column("Successes", justify="right", style="green")
        table.add_column("Failures", justify="right", style="red")
        table.add_column("Success Rate", justify="right")

        for provider, stats in report.provider_stats.items():
            total = stats['total']
            successes = stats['successes']
            failures = stats['failures']
            rate = (successes / total * 100) if total > 0 else 0

            rate_color = self._get_rate_color(rate)

            table.add_row(
                provider.title(),
                str(total),
                str(successes),
                str(failures),
                f"[{rate_color}]{rate:.1f}%[/]"
            )

        self.console.print(table)

    def _show_hourly_distribution(self, report: AnalyticsReport):
        """Display hourly activity distribution."""
        self.console.print("\n[bold cyan]⏰ Hourly Activity Distribution[/]\n")

        if not report.hourly_distribution:
            self.console.print("[yellow]No hourly data available[/]")
            return

        # Find max for scaling
        max_count = max(report.hourly_distribution.values()) if report.hourly_distribution else 1

        # Show as horizontal bars
        for hour in range(24):
            count = report.hourly_distribution.get(hour, 0)
            bar_length = int((count / max_count * 30)) if max_count > 0 else 0
            bar = "█" * bar_length

            hour_str = f"{hour:02d}:00"
            self.console.print(
                f"  {hour_str} [cyan]{bar}[/] {count}"
            )

    def _show_failure_analysis(self, report: AnalyticsReport):
        """Display failure analysis."""
        if not report.failure_reasons:
            return

        self.console.print("\n[bold cyan]⚠️  Failure Analysis[/]\n")

        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Error Reason", style="red")
        table.add_column("Count", justify="right", style="yellow")
        table.add_column("Percentage", justify="right")

        total_failures = sum(report.failure_reasons.values())

        for reason, count in sorted(
            report.failure_reasons.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            percentage = (count / total_failures * 100) if total_failures > 0 else 0
            table.add_row(
                reason or "Unknown",
                str(count),
                f"{percentage:.1f}%"
            )

        self.console.print(table)

    def show_provider_breakdown(self):
        """Show detailed provider breakdown."""
        if not self.console:
            return

        stats = self.analytics.get_provider_stats()

        self.console.print("\n[bold cyan]Provider Statistics[/]\n")

        for provider, data in stats.items():
            panel_content = f"""
            Total Events: [blue]{data['total_events']}[/]
            Successes: [green]{data['successes']}[/]
            Failures: [red]{data['failures']}[/]
            Success Rate: [{self._get_rate_color(data['success_rate'])}]{data['success_rate']}%[/]
            """

            self.console.print(
                Panel(
                    panel_content,
                    title=f"🔐 {provider.title()}",
                    border_style="cyan"
                )
            )

    def show_recent_events(self, count: int = 10):
        """
        Show recent events.

        Args:
            count: Number of events to show
        """
        if not self.console:
            return

        events = self.analytics.get_recent_events(count)

        self.console.print(f"\n[bold cyan]📝 Recent Events (Last {count})[/]\n")

        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Time", style="cyan")
        table.add_column("Event", style="yellow")
        table.add_column("Provider")
        table.add_column("Status")

        for event in events:
            time_str = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            status = "[green]✓[/]" if event.success else "[red]✗[/]"

            table.add_row(
                time_str,
                event.event_type,
                event.provider or "-",
                status
            )

        self.console.print(table)

    def export_report(self, filepath: str, period: str = 'last_24_hours'):
        """
        Export report to JSON file.

        Args:
            filepath: Path to export file
            period: Time period for the report
        """
        import json

        report = self.analytics.generate_report(period=period)

        data = {
            'period': period,
            'period_start': report.period_start.isoformat(),
            'period_end': report.period_end.isoformat(),
            'total_events': report.total_events,
            'login_attempts': report.login_attempts,
            'login_successes': report.login_successes,
            'login_failures': report.login_failures,
            'success_rate': report.success_rate,
            'avg_duration_ms': report.avg_duration_ms,
            'provider_stats': report.provider_stats,
            'failure_reasons': report.failure_reasons,
            'hourly_distribution': report.hourly_distribution,
            'daily_distribution': report.daily_distribution
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        if self.console:
            self.console.print(f"\n[green]✓ Report exported to {filepath}[/]")

    def _get_rate_color(self, rate: float) -> str:
        """Get color based on success rate."""
        if rate >= 95:
            return "green"
        elif rate >= 85:
            return "yellow"
        elif rate >= 70:
            return "orange3"
        else:
            return "red"
