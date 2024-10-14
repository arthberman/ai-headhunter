from datetime import UTC, datetime
from typing import Optional

from dateutil import parser

from analysis.models.profile import Profile


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


def format_date(date: Optional[str]) -> Optional[datetime]:
    """Format a date."""
    if not date or not is_valid_date(date):
        return None
    return parser.parse(date)


def compute_status(starts_at: Optional[datetime], ends_at: Optional[datetime]) -> str:
    """Compute the status of an experience or other time-based entry."""
    now = datetime.now(UTC)

    if not starts_at or starts_at.year <= 1900:
        return "Unknown status"

    if not ends_at or ends_at.year <= 1900:
        # Still ongoing
        duration = compute_duration(starts_at, now)
        return f"Ongoing for the last {duration}"

    if ends_at > now:
        # Future end date
        time_until_start = compute_duration(now, starts_at)
        return f"Starting in {time_until_start}"

    # Completed in the past
    duration = compute_duration(starts_at, ends_at)
    time_since_end = compute_duration(ends_at, now)
    return f"Lasted {duration} and ended {time_since_end} ago"


def get_profile_metadata(profile: Profile) -> Profile:
    """Enrich the profile with metadata."""
    for experience in profile.experiences:
        experience.metadata_duration = compute_duration(
            experience.startsAt, experience.endsAt
        )
        experience.metadata_status = compute_status(
            experience.startsAt, experience.endsAt
        )

    for education in profile.educations:
        education.metadata_duration = compute_duration(
            education.startsAt, education.endsAt
        )
        education.metadata_status = compute_status(education.startsAt, education.endsAt)

    for project in profile.projects:
        project.metadata_duration = compute_duration(project.startsAt, project.endsAt)
        project.metadata_status = compute_status(project.startsAt, project.endsAt)

    for volunteering in profile.volunteerings:
        volunteering.metadata_duration = compute_duration(
            volunteering.startsAt, volunteering.endsAt
        )
        volunteering.metadata_status = compute_status(
            volunteering.startsAt, volunteering.endsAt
        )

    return profile
