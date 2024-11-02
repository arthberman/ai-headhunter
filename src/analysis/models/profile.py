from datetime import datetime
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field


class ProfileEducation(BaseModel):
    """Profile education."""

    starts_at: Annotated[
        Optional[datetime], Field(description="Start date of education")
    ]
    ends_at: Annotated[
        Optional[datetime], Field(default=None, description="End date of education")
    ]
    school: Annotated[str, Field(description="School name")]
    field_of_study: Annotated[
        Optional[str], Field(default=None, description="Field of study")
    ]
    description: Annotated[
        Optional[str], Field(default=None, description="Education description")
    ]
    grade: Annotated[Optional[str], Field(default=None, description="Grade obtained")]
    degree: Annotated[Optional[str], Field(default=None, description="Degree obtained")]
    linkedin_url: Annotated[str, Field(description="LinkedIn URL of the school")]
    metadata_duration: Annotated[
        Optional[str], Field(default=None, description="Education duration")
    ]
    metadata_status: Annotated[
        Optional[str], Field(default=None, description="Education status")
    ]


class ProfileExperience(BaseModel):
    """Profile experience."""

    starts_at: Annotated[
        Optional[datetime], Field(description="Start date of experience")
    ]
    ends_at: Annotated[
        Optional[datetime], Field(default=None, description="End date of experience")
    ]
    company: Annotated[str, Field(description="Company name")]
    description: Annotated[
        Optional[str], Field(default=None, description="Experience description")
    ]
    title: Annotated[Optional[str], Field(default=None, description="Job title")]
    location: Annotated[Optional[str], Field(default=None, description="Job location")]
    linkedin_url: Annotated[str, Field(description="LinkedIn URL of the company")]
    employment_type: Annotated[
        Optional[str], Field(default=None, description="Employment type")
    ]
    metadata_duration: Annotated[
        Optional[str], Field(default=None, description="Education duration")
    ]
    metadata_status: Annotated[
        Optional[str], Field(default=None, description="Education status")
    ]


class ProfileVolunteering(BaseModel):
    """Profile volunteering."""

    starts_at: Annotated[
        Optional[datetime], Field(description="Start date of volunteering")
    ]
    ends_at: Annotated[
        Optional[datetime], Field(default=None, description="End date of volunteering")
    ]
    title: Annotated[
        Optional[str], Field(default=None, description="Volunteering title")
    ]
    description: Annotated[
        Optional[str], Field(default=None, description="Volunteering description")
    ]
    location: Annotated[
        Optional[str], Field(default=None, description="Volunteering location")
    ]
    metadata_duration: Annotated[
        Optional[str], Field(default=None, description="Education duration")
    ]
    metadata_status: Annotated[
        Optional[str], Field(default=None, description="Education status")
    ]


class ProfileHonor(BaseModel):
    """Profile honor."""

    title: Annotated[Optional[str], Field(description="Honor title")]
    description: Annotated[Optional[str], Field(description="Honor description")]
    issuer: Annotated[Optional[str], Field(description="Honor issuer")]
    issue_at: Annotated[Optional[datetime], Field(description="Date of honor issuance")]


class ProfileProject(BaseModel):
    """Profile project."""

    title: Annotated[Optional[str], Field(description="Project title")]
    description: Annotated[Optional[str], Field(description="Project description")]
    ends_at: Annotated[Optional[datetime], Field(description="Project end date")]
    starts_at: Annotated[Optional[datetime], Field(description="Project start date")]
    metadata_duration: Annotated[
        Optional[str], Field(default=None, description="Education duration")
    ]
    metadata_status: Annotated[
        Optional[str], Field(default=None, description="Education status")
    ]


class ProfileCertification(BaseModel):
    """Profile certification."""

    title: Annotated[Optional[str], Field(description="Certification title")]
    description: Annotated[
        Optional[str], Field(description="Certification description")
    ]
    issuer: Annotated[Optional[str], Field(description="Certification issuer")]
    issue_at: Annotated[
        Optional[datetime], Field(description="Date of certification issuance")
    ]


class ProfileLanguage(BaseModel):
    """Profile language."""

    language: Annotated[str, Field(description="Language name")]
    level: Annotated[str, Field(description="Language proficiency level")]


class ProfileAge(BaseModel):
    """Profile age."""

    range_lower_bound: Annotated[int, Field(description="Lower bound of the age range")]
    range_upper_bound: Annotated[int, Field(description="Upper bound of the age range")]
    explanation: Annotated[str, Field(description="Explanation for the age range")]
    confidence_score: Annotated[
        float, Field(description="Confidence score for the age range")
    ]


class Profile(BaseModel):
    """Profile."""

    id: Annotated[str, Field(description="Unique identifier for the profile")]
    country: Annotated[str, Field(description="Country of the profile")]
    city: Annotated[Optional[str], Field(description="City of the profile")]
    state: Annotated[Optional[str], Field(description="State of the profile")]
    headline: Annotated[Optional[str], Field(description="Headline of the profile")]
    summary: Annotated[Optional[str], Field(description="Summary of the profile")]
    connection_count: Annotated[
        Optional[int], Field(description="Number of connections")
    ]
    followers_count: Annotated[Optional[int], Field(description="Number of followers")]
    is_creator: Annotated[Optional[bool], Field(description="Is the profile a creator")]
    is_hiring: Annotated[Optional[bool], Field(description="Is the profile hiring")]
    is_open_to_work: Annotated[
        Optional[bool], Field(description="Is the profile open to work")
    ]
    linkedin_id: Annotated[str, Field(description="LinkedIn ID of the profile")]
    skills: Annotated[List[str], Field(description="List of skills")]
    certifications: Annotated[
        List[ProfileCertification], Field(description="List of certifications")
    ]
    educations: Annotated[
        List[ProfileEducation], Field(description="List of educations")
    ]
    experiences: Annotated[
        List[ProfileExperience], Field(description="List of experiences")
    ]
    honors: Annotated[List[ProfileHonor], Field(description="List of honors")]
    languages: Annotated[List[ProfileLanguage], Field(description="List of languages")]
    projects: Annotated[List[ProfileProject], Field(description="List of projects")]
    volunteerings: Annotated[
        List[ProfileVolunteering], Field(description="List of volunteering experiences")
    ]
    age_range: Annotated[
        Optional[ProfileAge],
        Field(default=None, description="Age range of the profile"),
    ]
