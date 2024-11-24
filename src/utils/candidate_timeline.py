from datetime import UTC, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from analysis.models.profile import Profile
from utils.get_profile_metadata import format_date


class TimelineFilter(Enum):
    """Filter options for timeline entries."""

    ALL = "all"
    EDUCATIONS = "educations"
    EXPERIENCES = "experiences"


class TimelineOverlap(BaseModel):
    """Represents an overlapping event in the timeline."""

    category: str
    description: str


class TimelineDates(BaseModel):
    """Date information for a timeline entry."""

    start: str = Field(..., description="ISO format date YYYY-MM-DD")
    end: Optional[str] = Field(
        None, description="ISO format date YYYY-MM-DD or None for ongoing"
    )
    duration: Optional[str] = None


class TimelineEntry(BaseModel):
    """A single entry in the candidate's timeline."""

    category: str
    description: str
    dates: TimelineDates
    status: Optional[str] = None
    location: Optional[str] = None
    details: Optional[str] = None
    employment_type: Optional[str] = None
    grade: Optional[str] = None
    overlaps: Optional[List[TimelineOverlap]] = None


class CandidateTimelineOutput(BaseModel):
    """Complete structured output for candidate timeline."""

    headline: Optional[str] = None
    summary: Optional[str] = None
    timeline: List[TimelineEntry]


def get_candidate_timeline(
    profile: Profile,
    with_detail: bool = False,
    filter_type: str = TimelineFilter.ALL.value,
) -> CandidateTimelineOutput:
    """Get a chronological timeline of the candidate's profile as structured JSON.

    Returns:
        Pydantic model containing structured timeline data
    """
    timeline_events = []

    # Add educations if filter allows
    if filter_type in [TimelineFilter.ALL.value, TimelineFilter.EDUCATIONS.value]:
        for edu in profile.educations:
            starts_at = format_date(edu.starts_at)
            if starts_at:
                ends_at = format_date(edu.ends_at)
                # Store None for computation if no end date
                computation_end = (
                    datetime.now(UTC)
                    if not ends_at or ends_at.year <= 1900
                    else ends_at
                )

                timeline_events.append(
                    (
                        starts_at,
                        computation_end,  # Use for overlap calculations
                        "Education",
                        f"{edu.degree or 'Study'} in {edu.field_of_study or 'N/A'} @ {edu.school}",
                        None,  # location
                        edu.metadata_duration,
                        edu.metadata_status,
                        edu.description,
                        None,  # employment_type
                        edu.grade,
                        ends_at
                        and ends_at.year
                        > 1900,  # Flag for whether we have a real end date
                    )
                )

    # Add experiences if filter allows
    if filter_type in [TimelineFilter.ALL.value, TimelineFilter.EXPERIENCES.value]:
        for exp in profile.experiences:
            starts_at = format_date(exp.starts_at)
            if starts_at:
                ends_at = format_date(exp.ends_at)
                # Store None for computation if no end date
                computation_end = (
                    datetime.now(UTC)
                    if not ends_at or ends_at.year <= 1900
                    else ends_at
                )

                timeline_events.append(
                    (
                        starts_at,
                        computation_end,  # Use for overlap calculations
                        "Experience",
                        f"{exp.title or 'Role'} @ {exp.company}",
                        exp.location,
                        exp.metadata_duration,
                        exp.metadata_status,
                        exp.description,
                        exp.employment_type,
                        None,  # grade
                        ends_at
                        and ends_at.year
                        > 1900,  # Flag for whether we have a real end date
                    )
                )

    # Sort by start date (reverse chronological)
    timeline_events.sort(key=lambda x: x[0], reverse=True)

    # Generate structured timeline entries
    timeline_entries = []
    for i, (
        start,
        computation_end,
        category,
        description,
        location,
        duration,
        status,
        details,
        employment_type,
        grade,
        has_end_date,
    ) in enumerate(timeline_events):
        # Create timeline entry
        entry_data = {
            "category": category,
            "description": description,
            "dates": {
                "start": start.strftime("%Y-%m-%d"),
                "end": computation_end.strftime("%Y-%m-%d") if has_end_date else None,
                "duration": duration,
            },
            "status": status,
            "location": location,
            "details": details if with_detail else None,
            "employment_type": employment_type if category == "Experience" else None,
            "grade": grade if category == "Education" else None,
        }

        # Check for overlaps if showing all entries
        if filter_type == TimelineFilter.ALL.value:
            overlaps = []
            for next_start, next_end, next_cat, next_desc, *_ in timeline_events[
                i + 1 :
            ]:
                if (next_start < computation_end) and (start < next_end):
                    overlaps.append(
                        TimelineOverlap(category=next_cat, description=next_desc)
                    )

            if overlaps:
                entry_data["overlaps"] = overlaps

        timeline_entries.append(TimelineEntry(**entry_data))

    return CandidateTimelineOutput(
        headline=profile.headline, summary=profile.summary, timeline=timeline_entries
    )
