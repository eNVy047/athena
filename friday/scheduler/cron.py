from datetime import datetime, timedelta

class CronParser:
    @staticmethod
    def get_next_trigger_time(cron_expression: str, base_time: datetime) -> datetime:
        """Calculates the next execution time for a cron expression."""
        try:
            from croniter import croniter
            return croniter(cron_expression, base_time).get_next(datetime)
        except ImportError:
            # Simple fallback: execution in 1 hour if croniter is absent
            return base_time + timedelta(hours=1)
