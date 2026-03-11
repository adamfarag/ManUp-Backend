from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


def today_str() -> str:
    """Return today's date as YYYY-MM-DD string in UTC."""
    return utc_now().strftime("%Y-%m-%d")


def date_str(dt: datetime) -> str:
    """Convert a datetime to a YYYY-MM-DD string."""
    return dt.strftime("%Y-%m-%d")
