"""
OAuth analytics tracking and metrics collection.

This module provides analytics and metrics tracking for OAuth 2.0 flows,
allowing you to monitor authentication patterns, success rates, and usage.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
from pathlib import Path


@dataclass
class OAuthEvent:
    """Represents a single OAuth event."""
    event_type: str
    timestamp: datetime
    provider: Optional[str] = None
    user_id: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'OAuthEvent':
        """Create event from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class AnalyticsReport:
    """Analytics report for a time period."""
    period_start: datetime
    period_end: datetime
    total_events: int
    login_attempts: int
    login_successes: int
    login_failures: int
    success_rate: float
    avg_duration_ms: float
    provider_stats: Dict[str, Dict[str, int]]
    failure_reasons: Dict[str, int]
    hourly_distribution: Dict[int, int]
    daily_distribution: Dict[str, int]


class OAuthAnalytics:
    """
    OAuth analytics and metrics tracker.

    Features:
    - Event tracking (login attempts, successes, failures)
    - Provider-specific metrics
    - Time-based analytics
    - Success rate monitoring
    - Performance tracking
    - Failure analysis

    Example:
        ```python
        from pauth.analytics import OAuthAnalytics

        analytics = OAuthAnalytics()

        # Track events
        analytics.track_event('login_attempt', provider='google')
        analytics.track_event('login_success', provider='google', user_id='123')

        # Generate reports
        report = analytics.generate_report(period='last_7_days')
        print(f"Success Rate: {report.success_rate}%")
        print(f"Total Logins: {report.login_successes}")

        # Get provider breakdown
        provider_stats = analytics.get_provider_stats()
        for provider, stats in provider_stats.items():
            print(f"{provider}: {stats['success_rate']}% success rate")
        ```
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize analytics tracker.

        Args:
            storage_path: Optional path to persist analytics data (JSON file)
        """
        self.events: List[OAuthEvent] = []
        self.storage_path = Path(storage_path) if storage_path else None

        if self.storage_path and self.storage_path.exists():
            self._load_events()

    def track_event(
        self,
        event_type: str,
        provider: Optional[str] = None,
        user_id: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        duration_ms: Optional[int] = None,
        **metadata
    ):
        """
        Track an OAuth event.

        Args:
            event_type: Type of event (login_attempt, login_success, login_failure, etc.)
            provider: OAuth provider name
            user_id: User identifier
            success: Whether the event was successful
            error: Error message if failed
            duration_ms: Duration in milliseconds
            **metadata: Additional metadata
        """
        event = OAuthEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            provider=provider,
            user_id=user_id,
            success=success,
            error=error,
            duration_ms=duration_ms,
            metadata=metadata
        )

        self.events.append(event)

        # Auto-save if storage is configured
        if self.storage_path:
            self._save_events()

    def generate_report(
        self,
        period: str = 'last_24_hours',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> AnalyticsReport:
        """
        Generate analytics report for a time period.

        Args:
            period: Predefined period ('last_24_hours', 'last_7_days', 'last_30_days', 'all_time')
            start_date: Custom start date (overrides period)
            end_date: Custom end date (overrides period)

        Returns:
            AnalyticsReport: Comprehensive analytics report
        """
        # Determine time range
        if start_date and end_date:
            period_start = start_date
            period_end = end_date
        else:
            period_start, period_end = self._get_period_range(period)

        # Filter events in period
        period_events = [
            e for e in self.events
            if period_start <= e.timestamp <= period_end
        ]

        # Calculate metrics
        total_events = len(period_events)
        login_attempts = len([e for e in period_events if 'login' in e.event_type.lower()])
        login_successes = len([
            e for e in period_events
            if e.event_type in ['login_success', 'login_attempt'] and e.success
        ])
        login_failures = len([
            e for e in period_events
            if e.event_type in ['login_failure', 'login_attempt'] and not e.success
        ])

        success_rate = (login_successes / login_attempts * 100) if login_attempts > 0 else 0

        # Average duration
        durations = [e.duration_ms for e in period_events if e.duration_ms is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Provider stats
        provider_stats = self._calculate_provider_stats(period_events)

        # Failure reasons
        failure_reasons = Counter([
            e.error for e in period_events
            if not e.success and e.error
        ])

        # Hourly distribution
        hourly_dist = defaultdict(int)
        for event in period_events:
            hourly_dist[event.timestamp.hour] += 1

        # Daily distribution
        daily_dist = defaultdict(int)
        for event in period_events:
            date_key = event.timestamp.strftime('%Y-%m-%d')
            daily_dist[date_key] += 1

        return AnalyticsReport(
            period_start=period_start,
            period_end=period_end,
            total_events=total_events,
            login_attempts=login_attempts,
            login_successes=login_successes,
            login_failures=login_failures,
            success_rate=round(success_rate, 2),
            avg_duration_ms=round(avg_duration, 2),
            provider_stats=provider_stats,
            failure_reasons=dict(failure_reasons),
            hourly_distribution=dict(hourly_dist),
            daily_distribution=dict(daily_dist)
        )

    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics broken down by provider.

        Returns:
            dict: Provider statistics
        """
        provider_events = defaultdict(list)

        for event in self.events:
            if event.provider:
                provider_events[event.provider].append(event)

        stats = {}
        for provider, events in provider_events.items():
            total = len(events)
            successes = len([e for e in events if e.success])
            failures = total - successes
            success_rate = (successes / total * 100) if total > 0 else 0

            stats[provider] = {
                'total_events': total,
                'successes': successes,
                'failures': failures,
                'success_rate': round(success_rate, 2)
            }

        return stats

    def get_recent_events(self, count: int = 10) -> List[OAuthEvent]:
        """
        Get most recent events.

        Args:
            count: Number of events to return

        Returns:
            list: Recent events
        """
        return sorted(self.events, key=lambda e: e.timestamp, reverse=True)[:count]

    def get_failure_analysis(self) -> Dict[str, Any]:
        """
        Analyze failure patterns.

        Returns:
            dict: Failure analysis
        """
        failures = [e for e in self.events if not e.success]

        if not failures:
            return {
                'total_failures': 0,
                'by_provider': {},
                'by_error': {},
                'failure_rate': 0
            }

        # Group by provider
        by_provider = Counter([e.provider for e in failures if e.provider])

        # Group by error
        by_error = Counter([e.error for e in failures if e.error])

        # Calculate failure rate
        total_events = len(self.events)
        failure_rate = (len(failures) / total_events * 100) if total_events > 0 else 0

        return {
            'total_failures': len(failures),
            'by_provider': dict(by_provider),
            'by_error': dict(by_error),
            'failure_rate': round(failure_rate, 2)
        }

    def clear_events(self, older_than_days: Optional[int] = None):
        """
        Clear old events.

        Args:
            older_than_days: Clear events older than this many days (if None, clears all)
        """
        if older_than_days is None:
            self.events = []
        else:
            cutoff = datetime.utcnow() - timedelta(days=older_than_days)
            self.events = [e for e in self.events if e.timestamp > cutoff]

        if self.storage_path:
            self._save_events()

    def _get_period_range(self, period: str) -> tuple:
        """Get start and end dates for predefined periods."""
        now = datetime.utcnow()

        if period == 'last_24_hours':
            return now - timedelta(hours=24), now
        elif period == 'last_7_days':
            return now - timedelta(days=7), now
        elif period == 'last_30_days':
            return now - timedelta(days=30), now
        elif period == 'all_time':
            return datetime.min, now
        else:
            # Default to last 24 hours
            return now - timedelta(hours=24), now

    def _calculate_provider_stats(self, events: List[OAuthEvent]) -> Dict[str, Dict[str, int]]:
        """Calculate statistics per provider."""
        provider_stats = defaultdict(lambda: {
            'total': 0,
            'successes': 0,
            'failures': 0
        })

        for event in events:
            if event.provider:
                provider_stats[event.provider]['total'] += 1
                if event.success:
                    provider_stats[event.provider]['successes'] += 1
                else:
                    provider_stats[event.provider]['failures'] += 1

        return dict(provider_stats)

    def _save_events(self):
        """Save events to storage."""
        if not self.storage_path:
            return

        data = [event.to_dict() for event in self.events]

        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_events(self):
        """Load events from storage."""
        if not self.storage_path or not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            self.events = [OAuthEvent.from_dict(event_data) for event_data in data]
        except Exception as e:
            # If loading fails, start with empty events
            self.events = []

    def export_to_csv(self, filepath: str):
        """
        Export events to CSV file.

        Args:
            filepath: Path to CSV file
        """
        import csv

        with open(filepath, 'w', newline='') as f:
            if not self.events:
                return

            fieldnames = ['timestamp', 'event_type', 'provider', 'user_id', 'success', 'error', 'duration_ms']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for event in self.events:
                writer.writerow({
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.event_type,
                    'provider': event.provider,
                    'user_id': event.user_id,
                    'success': event.success,
                    'error': event.error,
                    'duration_ms': event.duration_ms
                })
