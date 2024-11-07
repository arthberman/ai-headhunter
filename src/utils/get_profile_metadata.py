from analysis.models.profile import Profile
from utils.time import compute_duration, compute_status, format_date


def get_profile_metadata(profile: Profile) -> Profile:
    """Enrich the profile with metadata."""
    for experience in profile.experiences:
        # Format the dates first
        formatted_start = format_date(experience.starts_at)
        formatted_end = format_date(experience.ends_at)

        experience.metadata_duration = compute_duration(formatted_start, formatted_end)
        experience.metadata_status = compute_status(formatted_start, formatted_end)

    for education in profile.educations:
        formatted_start = format_date(education.starts_at)
        formatted_end = format_date(education.ends_at)

        education.metadata_duration = compute_duration(formatted_start, formatted_end)
        education.metadata_status = compute_status(formatted_start, formatted_end)

    for project in profile.projects:
        formatted_start = format_date(project.starts_at)
        formatted_end = format_date(project.ends_at)

        project.metadata_duration = compute_duration(formatted_start, formatted_end)
        project.metadata_status = compute_status(formatted_start, formatted_end)

    for volunteering in profile.volunteerings:
        formatted_start = format_date(volunteering.starts_at)
        formatted_end = format_date(volunteering.ends_at)

        volunteering.metadata_duration = compute_duration(
            formatted_start, formatted_end
        )
        volunteering.metadata_status = compute_status(formatted_start, formatted_end)

    return profile
