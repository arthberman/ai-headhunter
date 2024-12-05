from datetime import UTC, datetime
from typing import Optional

from dateutil import parser


def compute_duration(
    start_date: Optional[datetime], end_date: Optional[datetime]
) -> str:
    """Compute the duration between two dates in years and months format.

    Examples:
        - 1 year and 2 months -> "1y2m"
        - 2 years -> "2y"
        - 1 year and 11 months -> "1y11m"
        - 3 months -> "3m"
    """
    if not start_date or start_date.year <= 1900:
        return "Unknown duration"

    if not end_date or end_date.year <= 1900:
        end_date = datetime.now(UTC)

    delta = end_date - start_date
    years, remainder = divmod(delta.days, 365)
    months = round(remainder / 30.44)  # Average days in a month

    # Adjust for rounding up to 12 months
    if months == 12:
        years += 1
        months = 0

    if years > 0 and months > 0:
        return f"{years}y{months}m"
    elif years > 0:
        return f"{years}y"
    elif months > 0:
        return f"{months}m"
    else:
        return "1m"  # Minimum duration shown


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


def compute_status(start_date: Optional[datetime], end_date: Optional[datetime]) -> str:
    """Compute the status of an experience or other time-based entry."""
    now = datetime.now(UTC)

    if not start_date or start_date.year <= 1900:
        return "Unknown status"

    if not end_date or end_date.year <= 1900:
        # Still ongoing
        return "Ongoing"

    if end_date > now:
        # Future end date
        time_until_start = compute_duration(now, start_date)
        return f"Starting in {time_until_start}"

    # Completed in the past
    duration = compute_duration(start_date, end_date)
    time_since_end = compute_duration(end_date, now)
    return f"Lasted {duration} and ended {time_since_end} ago"
