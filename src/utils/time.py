from datetime import UTC, datetime
from typing import Optional

from dateutil import parser


def compute_duration(starts_at: Optional[datetime], ends_at: Optional[datetime]) -> str:
    """Compute the duration between two dates."""
    if not starts_at or starts_at.year <= 1900:
        return "Unknown duration"

    if not ends_at or ends_at.year <= 1900:
        ends_at = datetime.now(UTC)

    delta = ends_at - starts_at
    years, remainder = divmod(delta.days, 365)
    months = remainder // 30

    # Adjust for potential rounding issues
    if months == 12:
        years += 1
        months = 0

    if years > 0 and months > 0:
        return f"{years} year{'s' if years > 1 else ''} {months} month{'s' if months > 1 else ''}"
    elif years > 0:
        return f"{years} year{'s' if years > 1 else ''}"
    elif months > 0:
        return f"{months} month{'s' if months > 1 else ''}"
    else:
        return "Less than a month"


def is_valid_date(date: str) -> bool:
    """Check if a date is valid."""
    try:
        parsed_date = parser.parse(date)
        return parsed_date.year > 1900
    except ValueError:
        return False


def format_date(date: Optional[str | datetime]) -> Optional[datetime]:
    """Format a date string or datetime object into a datetime."""
    if not date:
        return None

    # If it's already a datetime object, just return it
    if isinstance(date, datetime):
        return date

    # Otherwise, try to parse the string
    if not is_valid_date(date):
        return None

    return parser.parse(date)


def compute_status(starts_at: Optional[datetime], ends_at: Optional[datetime]) -> str:
    """Compute the status of an experience or other time-based entry."""
    now = datetime.now(UTC)

    if not starts_at or starts_at.year <= 1900:
        return "Unknown status"

    if not ends_at or ends_at.year <= 1900:
        # Still ongoing
        return "Ongoing"

    if ends_at > now:
        # Future end date
        time_until_start = compute_duration(now, starts_at)
        return f"Starting in {time_until_start}"

    # Completed in the past
    duration = compute_duration(starts_at, ends_at)
    time_since_end = compute_duration(ends_at, now)
    return f"Lasted {duration} and ended {time_since_end} ago"
