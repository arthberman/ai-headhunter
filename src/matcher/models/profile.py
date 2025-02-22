from typing import List, Optional

from pydantic import BaseModel, Field


class DateModel(BaseModel):
    """Date model with year and optional month."""

    year: int = Field(description="Year of the date")
    month: Optional[int] = Field(default=None, description="Month of the date")


class ProfileEducation(BaseModel):
    """Profile education."""

    start_date: Optional[DateModel] = Field(
        default=None, description="Start date of education"
    )
    end_date: Optional[DateModel] = Field(
        default=None, description="End date of education"
    )
    school: str = Field(description="School name")
    field_of_study: Optional[str] = Field(default=None, description="Field of study")
    description: Optional[str] = Field(
        default=None, description="Education description"
    )
    grade: Optional[str] = Field(default=None, description="Grade obtained")
    degree: Optional[str] = Field(default=None, description="Degree obtained")
    linkedin_id: str = Field(description="LinkedIn ID of the school")
    metadata_duration: Optional[str] = Field(
        default=None, description="Education duration"
    )
    metadata_status: Optional[str] = Field(default=None, description="Education status")


class ProfileExperience(BaseModel):
    """Profile experience."""

    start_date: Optional[DateModel] = Field(
        default=None, description="Start date of experience"
    )
    end_date: Optional[DateModel] = Field(
        default=None, description="End date of experience"
    )
    company: str = Field(description="Company name")
    description: Optional[str] = Field(
        default=None, description="Experience description"
    )
    title: Optional[str] = Field(default=None, description="Job title")
    location: Optional[str] = Field(default=None, description="Job location")
    linkedin_id: str = Field(description="LinkedIn ID of the company")
    employment_type: Optional[str] = Field(default=None, description="Employment type")
    metadata_duration: Optional[str] = Field(
        default=None, description="Education duration"
    )
    metadata_status: Optional[str] = Field(default=None, description="Education status")


class ProfileVolunteering(BaseModel):
    """Profile volunteering."""

    start_date: Optional[DateModel] = Field(description="Start date of volunteering")
    end_date: Optional[DateModel] = Field(
        default=None, description="End date of volunteering"
    )
    title: Optional[str] = Field(default=None, description="Volunteering title")
    description: Optional[str] = Field(
        default=None, description="Volunteering description"
    )
    location: Optional[str] = Field(default=None, description="Volunteering location")
    metadata_duration: Optional[str] = Field(
        default=None, description="Education duration"
    )
    metadata_status: Optional[str] = Field(default=None, description="Education status")


class ProfileHonor(BaseModel):
    """Profile honor."""

    title: Optional[str] = Field(description="Honor title")
    description: Optional[str] = Field(description="Honor description")
    issuer: Optional[str] = Field(description="Honor issuer")
    issue_at: Optional[DateModel] = Field(description="Date of honor issuance")


class ProfileProject(BaseModel):
    """Profile project."""

    title: Optional[str] = Field(description="Project title")
    description: Optional[str] = Field(description="Project description")
    end_date: Optional[DateModel] = Field(description="Project end date")
    start_date: Optional[DateModel] = Field(description="Project start date")
    metadata_duration: Optional[str] = Field(
        default=None, description="Education duration"
    )
    metadata_status: Optional[str] = Field(default=None, description="Education status")


class ProfileCertification(BaseModel):
    """Profile certification."""

    title: Optional[str] = Field(default=None, description="Certification title")
    description: Optional[str] = Field(
        default=None, description="Certification description"
    )
    issuer: Optional[str] = Field(default=None, description="Certification issuer")
    issue_at: Optional[DateModel] = Field(
        default=None, description="Date of certification issuance"
    )


class ProfileLanguage(BaseModel):
    """Profile language."""

    language: str = Field(description="Language name")
    level: str = Field(description="Language proficiency level")


class ProfileAge(BaseModel):
    """Profile age."""

    lower: int = Field(description="Lower bound of the age range")
    upper: int = Field(description="Upper bound of the age range")
    explanation: str = Field(description="Explanation for the age range")
    confidence: float = Field(description="Confidence score for the age range")


class Profile(BaseModel):
    """Profile."""

    id: str = Field(description="Unique identifier for the profile")
    location: str = Field(description="Location of the profile (city, country)")
    headline: Optional[str] = Field(default=None, description="Headline of the profile")
    summary: Optional[str] = Field(default=None, description="Summary of the profile")
    connection_count: Optional[int] = Field(
        default=None, description="Number of connections"
    )
    followers_count: Optional[int] = Field(
        default=None, description="Number of followers"
    )
    is_creator: Optional[bool] = Field(
        default=None, description="Is the profile a creator"
    )
    is_hiring: Optional[bool] = Field(default=None, description="Is the profile hiring")
    is_open_to_work: Optional[bool] = Field(
        default=None, description="Is the profile open to work"
    )
    linkedin_urn: str = Field(description="LinkedIn URN of the profile")
    linkedin_slug: str = Field(description="LinkedIn slug of the profile")
    skills: List[str] = Field(description="List of skills")
    certifications: List[ProfileCertification] = Field(
        description="List of certifications"
    )
    educations: List[ProfileEducation] = Field(description="List of educations")
    experiences: List[ProfileExperience] = Field(description="List of experiences")
    honors: List[ProfileHonor] = Field(description="List of honors")
    languages: List[ProfileLanguage] = Field(description="List of languages")
    projects: List[ProfileProject] = Field(description="List of projects")
    volunteerings: List[ProfileVolunteering] = Field(
        description="List of volunteering experiences"
    )
    age_range: Optional[ProfileAge] = Field(
        default=None, description="Age range of the profile"
    )
