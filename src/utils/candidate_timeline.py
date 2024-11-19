from datetime import UTC, datetime
from enum import Enum
from typing import List, Optional, Tuple

from analysis.models.profile import Profile
from utils.get_profile_metadata import format_date


class TimelineFilter(Enum):
    """Filter options for timeline entries."""

    ALL = "all"
    EDUCATIONS = "educations"
    EXPERIENCES = "experiences"


def get_candidate_timeline(
    profile: Profile,
    with_detail: bool = False,
    filter_type: str = TimelineFilter.ALL.value,
) -> str:
    """Get a chronological timeline of the candidate's profile."""
    output = []
    output.append("Candidate Timeline")

    # Add headline if available
    if profile.headline:
        output.append(f"Headline: {profile.headline}")
        output.append("")

    # Add summary if available
    if profile.summary:
        output.append("Summary:")
        summary_lines = profile.summary.split("\n")
        for line in summary_lines:
            if line.strip():
                output.append(f"    {line.strip()}")
        output.append("")

    timeline_events: List[
        Tuple[
            datetime,
            datetime,
            str,
            str,
            Optional[str],
            Optional[str],
            Optional[str],
            Optional[str],
            Optional[str],
            Optional[str],  # grade
        ]
    ] = []

    # Add educations if filter allows
    if filter_type in [TimelineFilter.ALL.value, TimelineFilter.EDUCATIONS.value]:
        for edu in profile.educations:
            starts_at = format_date(edu.starts_at)
            if starts_at:
                ends_at = format_date(edu.ends_at)
                if not ends_at or ends_at.year <= 1900:
                    ends_at = datetime.now(UTC)

                timeline_events.append(
                    (
                        starts_at,
                        ends_at,
                        "Education",
                        f"{edu.degree or 'Study'} in {edu.field_of_study or 'N/A'} @ {edu.school}",
                        None,  # location
                        edu.metadata_duration,
                        edu.metadata_status,
                        edu.description,
                        None,  # employment_type
                        edu.grade,
                    )
                )

    # Add experiences if filter allows
    if filter_type in [TimelineFilter.ALL.value, TimelineFilter.EXPERIENCES.value]:
        for exp in profile.experiences:
            starts_at = format_date(exp.starts_at)
            if starts_at:
                ends_at = format_date(exp.ends_at)
                if not ends_at or ends_at.year <= 1900:
                    ends_at = datetime.now(UTC)

                timeline_events.append(
                    (
                        starts_at,
                        ends_at,
                        "Experience",
                        f"{exp.title or 'Role'} @ {exp.company}",
                        exp.location,
                        exp.metadata_duration,
                        exp.metadata_status,
                        exp.description,
                        exp.employment_type,
                        None,  # grade
                    )
                )

    # Sort by start date (reverse chronological)
    timeline_events.sort(key=lambda x: x[0], reverse=True)

    # Generate output
    for i, (
        start,
        end,
        category,
        description,
        location,
        duration,
        status,
        details,
        employment_type,
        grade,
    ) in enumerate(timeline_events):
        # Format date range for display and bracket
        end_date_str = "Present" if end == datetime.now(UTC) else end.strftime("%b %Y")
        date_bracket = f"[{start.strftime('%b %Y')} - {end_date_str}]"

        # Build the entry line with all available metadata
        entry_parts = [f"• [{category}] {description}"]

        if location:
            entry_parts.append(f"- {location}")
        if category == "Experience" and employment_type:
            entry_parts.append(f"({employment_type})")
        if category == "Education" and grade:
            entry_parts.append(f"[Grade: {grade}]")

        entry_parts.append(date_bracket)
        output.append(" ".join(entry_parts))

        # Add metadata on a new line if available
        metadata_parts = []
        if duration:
            metadata_parts.append(f"Duration: {duration}")
        if status:
            metadata_parts.append(f"Status: {status}")
        if metadata_parts:
            output.append(f"    ⌊ {' | '.join(metadata_parts)}")

        # Add description if with_detail is True
        if with_detail and details:
            detail_lines = details.split("\n")
            for line in detail_lines:
                if line.strip():
                    output.append(f"    ↳ {line.strip()}")

        # Check for overlaps only if showing all entries
        if filter_type == TimelineFilter.ALL:
            overlaps = []
            for (
                next_start,
                next_end,
                next_cat,
                next_desc,
                _,
                _,
                _,
                _,
                _,
                _,
            ) in timeline_events[i + 1 :]:
                if (next_start < end) and (start < next_end):
                    overlaps.append(f"[{next_cat}] {next_desc}")

            if overlaps:
                output.append(f"  (Overlaps with: {', '.join(overlaps)})")

        output.append("")

    return "\n".join(output).rstrip()
