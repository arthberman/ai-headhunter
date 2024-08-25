import json
from datetime import datetime

from matcher.models.profile import (
    Profile,
    ProfileCertification,
    ProfileEducation,
    ProfileExperience,
    ProfileHonor,
    ProfileLanguage,
    ProfileProject,
    ProfileVolunteering,
)


def parseProfile(profile: json) -> Profile:
    """Convert a raw JSON object to a Profile object"""

    # Convert experiences
    experiences = [
        ProfileExperience(
            startsAt=datetime.fromisoformat(exp["startsAt"]),
            endsAt=(
                datetime.fromisoformat(exp["endsAt"])
                if exp["endsAt"] != "1899-12-30T23:50:39.000Z"
                else None
            ),
            company=exp["company"]["name"],
            description=exp["description"],
            title=exp["title"],
            location=exp["location"],
            linkedin_url=exp["company"]["linkedinUrl"],
        )
        for exp in profile.get("experiences", [])
    ]

    # Convert educations
    educations = [
        ProfileEducation(
            startsAt=datetime.fromisoformat(edu["startsAt"]),
            endsAt=datetime.fromisoformat(edu["endsAt"]),
            school=edu["school"]["name"],
            description=edu["description"],
            fieldOfStudy=edu["fieldOfStudy"],
            grade=edu["grade"],
            degree=edu["degree"],
            linkedin_url=edu["school"]["linkedinUrl"],
        )
        for edu in profile.get("educations", [])
    ]

    # Convert certifications
    certifications = [
        ProfileCertification(
            title=cert["title"],
            description=cert["description"],
            issuer=cert["issuer"],
            issueAt=datetime.fromisoformat(cert["issueAt"]),
        )
        for cert in profile.get("certifications", [])
    ]

    # Convert languages
    languages = [
        ProfileLanguage(language=lang["language"], level=lang["level"])
        for lang in profile.get("languages", [])
    ]

    # Convert projects
    projects = [
        ProfileProject(
            title=proj["title"],
            description=proj["description"],
            contributors=proj["contributors"],
            endsAt=datetime.fromisoformat(proj["endsAt"]),
            startsAt=datetime.fromisoformat(proj["startsAt"]),
        )
        for proj in profile.get("projects", [])
    ]

    # Convert volunteerings
    volunteerings = [
        ProfileVolunteering(
            startsAt=datetime.fromisoformat(vol["startsAt"]),
            endsAt=datetime.fromisoformat(vol["endsAt"]),
            title=vol["title"],
            description=vol["description"],
            location=vol["location"],
        )
        for vol in profile.get("volunteerings", [])
    ]

    # Convert honors
    honors = [
        ProfileHonor(
            title=honor["title"],
            description=honor["description"],
            issuer=honor["issuer"],
            issueAt=datetime.fromisoformat(honor["issueAt"]),
        )
        for honor in profile.get("honors", [])
    ]

    # Create the Profile object
    profile = Profile(
        id=profile["id"],
        country=profile["country"],
        city=profile["city"],
        state=profile["state"],
        headline=profile["headline"],
        summary=profile["summary"],
        connectionCount=profile["connectionCount"],
        followersCount=profile["followersCount"],
        isCreator=profile["isCreator"],
        isHiring=profile["isHiring"],
        isOpenToWork=profile["isOpenToWork"],
        linkedin_id=profile["linkedin_id"],
        skills=profile["skills"],
        certifications=certifications,
        educations=educations,
        experiences=experiences,
        honors=honors,
        languages=languages,
        projects=projects,
        volunteerings=volunteerings,
    )

    return profile
