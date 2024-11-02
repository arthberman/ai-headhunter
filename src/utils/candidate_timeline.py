from datetime import datetime
from typing import List, Tuple

from analysis.models.profile import Profile


def get_candidate_timeline(profile: Profile) -> str:
    """Get a chronological timeline of the candidate's profile."""
    # Collect all timeline events
    timeline_events: List[Tuple[datetime, datetime, str, str]] = []

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
                )
            )

    # Sort by start date (reverse chronological)
    timeline_events.sort(key=lambda x: x[0], reverse=True)

    # Generate output
    output = []
    for i, (start, end, category, description) in enumerate(timeline_events):
        # Format date range
        date_str = f"{start.strftime('%b %Y')} - {end.strftime('%b %Y') if end != datetime.now() else 'Present'}"

        # Add main entry
        output.append(f"• [{category}] {description} ({date_str})")

        # Check for overlaps with subsequent events
        overlaps = []
        for next_start, next_end, next_cat, next_desc in timeline_events[i + 1 :]:
            # Only consider it an overlap if one event starts before another ends
            # and the other event starts before this one ends
            if (next_start < end) and (start < next_end):
                overlaps.append(f"[{next_cat}] {next_desc}")

        if overlaps:
            output.append(f"  (Overlaps with: {', '.join(overlaps)})")

    return "\n".join(output)
