from datetime import datetime
from typing import List, Optional, Tuple

from analysis.models.profile import Profile


def get_candidate_timeline(profile: Profile, with_detail: bool = False) -> str:
    """Get a chronological timeline of the candidate's profile."""
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
        ]
    ] = []

    # Add educations
    for edu in profile.educations:
        if edu.starts_at:
            end_date = (
                edu.ends_at
                if (edu.ends_at and edu.ends_at.year > 1900)
                else datetime.now()
            )
            timeline_events.append(
                (
                    edu.starts_at,
                    end_date,
                    "Education",
                    f"{edu.degree or 'Study'} in {edu.field_of_study or 'N/A'} @ {edu.school}",
                    None,  # Location not typically available for education
                    edu.metadata_duration,
                    edu.metadata_status,
                    edu.description,
                )
            )

    # Add experiences
    for exp in profile.experiences:
        if exp.starts_at:
            end_date = (
                exp.ends_at
                if (exp.ends_at and exp.ends_at.year > 1900)
                else datetime.now()
            )
            timeline_events.append(
                (
                    exp.starts_at,
                    end_date,
                    "Experience",
                    f"{exp.title or 'Role'} @ {exp.company}",
                    exp.location,
                    exp.metadata_duration,
                    exp.metadata_status,
                    exp.description,
                )
            )

    # Sort by start date (reverse chronological)
    timeline_events.sort(key=lambda x: x[0], reverse=True)

    # Generate output
    output = []
    for i, (
        start,
        end,
        category,
        description,
        location,
        duration,
        status,
        details,
    ) in enumerate(timeline_events):
        # Format date range for display and bracket
        end_date_str = "Present" if end == datetime.now() else end.strftime("%b %Y")
        date_bracket = f"[{start.strftime('%b %Y')} - {end_date_str}"
        if duration:
            date_bracket += f" / {duration}"
        date_bracket += "]"

        # Build the entry line with all available metadata
        entry_parts = [f"• [{category}] {description}"]
        if location:
            entry_parts.append(f"- {location}")
        entry_parts.append(date_bracket)
        if status:
            entry_parts.append(f"- {status}")

        output.append(" ".join(entry_parts))

        # Add description if with_detail is True
        if with_detail and details:
            detail_lines = details.split("\n")
            for line in detail_lines:
                if line.strip():
                    output.append(f"    ↳ {line.strip()}")

        # Check for overlaps
        overlaps = []
        for next_start, next_end, next_cat, next_desc, _, _, _, _ in timeline_events[
            i + 1 :
        ]:
            if (next_start < end) and (start < next_end):
                overlaps.append(f"[{next_cat}] {next_desc}")

        if overlaps:
            output.append(f"  (Overlaps with: {', '.join(overlaps)})")

        output.append("")

    return "\n".join(output).rstrip()
