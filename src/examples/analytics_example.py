"""
OAuth Analytics Example

This example demonstrates using the analytics tracker and dashboard
to monitor OAuth authentication metrics.

Requirements:
- pip install rich (for dashboard visualization)

Usage:
    python analytics_example.py
"""

import time
import random
from datetime import datetime, timedelta

from src.analytics import OAuthAnalytics, AnalyticsDashboard


def simulate_oauth_events(analytics: OAuthAnalytics, num_events: int = 100):
    """
    Simulate OAuth events for demonstration.

    Args:
        analytics: OAuthAnalytics instance
        num_events: Number of events to simulate
    """
    print(f"Simulating {num_events} OAuth events...")

    providers = ['google', 'github', 'facebook', 'twitter', 'microsoft']
    event_types = ['login_attempt', 'login_success', 'login_failure', 'token_refresh']
    errors = [None, 'invalid_code', 'expired_token', 'network_error', 'invalid_state']

    for i in range(num_events):
        provider = random.choice(providers)
        event_type = random.choice(event_types)

        # Simulate realistic success rates
        success = random.random() > 0.15  # 85% success rate

        # Add error for failures
        error = None if success else random.choice(errors[1:])

        # Simulate response time
        duration_ms = random.randint(100, 2000)

        # Track the event
        analytics.track_event(
            event_type=event_type,
            provider=provider,
            user_id=f"user_{random.randint(1, 50)}",
            success=success,
            error=error,
            duration_ms=duration_ms
        )

        # Small delay for realistic timing
        if i % 10 == 0:
            time.sleep(0.01)

    print(f"✓ Generated {num_events} events\n")


def demo_basic_tracking():
    """Demonstrate basic analytics tracking."""
    print("\n" + "=" * 60)
    print("Demo 1: Basic Event Tracking")
    print("=" * 60 + "\n")

    # Initialize analytics
    analytics = OAuthAnalytics()

    # Track some events
    print("Tracking events...")

    analytics.track_event('login_attempt', provider='google')
    analytics.track_event('login_success', provider='google', user_id='user123', duration_ms=450)

    analytics.track_event('login_attempt', provider='github')
    analytics.track_event('login_failure', provider='github', error='invalid_code')

    analytics.track_event('login_attempt', provider='facebook')
    analytics.track_event('login_success', provider='facebook', user_id='user456', duration_ms=620)

    # Generate report
    report = analytics.generate_report(period='all_time')

    print(f"\nTotal Events: {report.total_events}")
    print(f"Login Attempts: {report.login_attempts}")
    print(f"Successful Logins: {report.login_successes}")
    print(f"Failed Logins: {report.login_failures}")
    print(f"Success Rate: {report.success_rate}%")
    print(f"Average Duration: {report.avg_duration_ms:.0f}ms")


def demo_dashboard():
    """Demonstrate the analytics dashboard."""
    print("\n" + "=" * 60)
    print("Demo 2: Analytics Dashboard")
    print("=" * 60 + "\n")

    # Initialize analytics
    analytics = OAuthAnalytics(storage_path='demo_analytics.json')

    # Simulate a day's worth of events
    simulate_oauth_events(analytics, num_events=200)

    # Create and show dashboard
    dashboard = AnalyticsDashboard(analytics)
    dashboard.show(period='all_time')


def demo_provider_stats():
    """Demonstrate provider-specific statistics."""
    print("\n" + "=" * 60)
    print("Demo 3: Provider Statistics")
    print("=" * 60 + "\n")

    analytics = OAuthAnalytics()

    # Simulate events for different providers
    simulate_oauth_events(analytics, num_events=150)

    # Get provider stats
    provider_stats = analytics.get_provider_stats()

    print("Provider Breakdown:\n")
    for provider, stats in provider_stats.items():
        print(f"{provider.title()}:")
        print(f"  Total Events: {stats['total_events']}")
        print(f"  Successes: {stats['successes']}")
        print(f"  Failures: {stats['failures']}")
        print(f"  Success Rate: {stats['success_rate']}%")
        print()


def demo_failure_analysis():
    """Demonstrate failure analysis."""
    print("\n" + "=" * 60)
    print("Demo 4: Failure Analysis")
    print("=" * 60 + "\n")

    analytics = OAuthAnalytics()

    # Simulate events with various failures
    simulate_oauth_events(analytics, num_events=100)

    # Get failure analysis
    failure_analysis = analytics.get_failure_analysis()

    print(f"Total Failures: {failure_analysis['total_failures']}")
    print(f"Failure Rate: {failure_analysis['failure_rate']}%\n")

    print("Failures by Provider:")
    for provider, count in failure_analysis['by_provider'].items():
        print(f"  {provider}: {count}")

    print("\nFailures by Error Type:")
    for error, count in failure_analysis['by_error'].items():
        print(f"  {error}: {count}")


def demo_export():
    """Demonstrate data export."""
    print("\n" + "=" * 60)
    print("Demo 5: Data Export")
    print("=" * 60 + "\n")

    analytics = OAuthAnalytics()
    simulate_oauth_events(analytics, num_events=50)

    # Export to CSV
    csv_file = 'oauth_analytics.csv'
    analytics.export_to_csv(csv_file)
    print(f"✓ Exported events to {csv_file}")

    # Export report to JSON
    dashboard = AnalyticsDashboard(analytics)
    json_file = 'analytics_report.json'
    dashboard.export_report(json_file, period='all_time')
    print(f"✓ Exported report to {json_file}")


def main():
    """Run all analytics examples."""
    print("╔════════════════════════════════════════════════════════╗")
    print("║   PAuth Analytics & Dashboard - Examples              ║")
    print("╚════════════════════════════════════════════════════════╝")

    # Run demos
    demo_basic_tracking()
    demo_provider_stats()
    demo_failure_analysis()
    demo_export()

    # Show interactive dashboard (requires Rich)
    try:
        demo_dashboard()
    except ImportError:
        print("\nNote: Install 'rich' for interactive dashboard:")
        print("  pip install rich")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("""
You can integrate analytics into your OAuth flows:

    from pauth.analytics import OAuthAnalytics, AnalyticsDashboard

    analytics = OAuthAnalytics(storage_path='analytics.json')

    # Track events during OAuth flow
    analytics.track_event('login_attempt', provider='google')
    # ... perform OAuth ...
    analytics.track_event('login_success', provider='google', user_id='123')

    # View dashboard
    dashboard = AnalyticsDashboard(analytics)
    dashboard.show(period='last_24_hours')
    """)


if __name__ == "__main__":
    main()
