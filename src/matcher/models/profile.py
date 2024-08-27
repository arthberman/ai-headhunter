from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

from langchain.pydantic_v1 import BaseModel, Field


class ProfileEducation(BaseModel):
    startsAt: Annotated[datetime, Field(description="Start date of education")]
    endsAt: Annotated[Optional[datetime], Field(description="End date of education")]
    school: Annotated[str, Field(description="School name")]
    fieldOfStudy: Annotated[Optional[str], Field(description="Field of study")]
    description: Annotated[Optional[str], Field(description="Education description")]
    grade: Annotated[Optional[str], Field(description="Grade obtained")]
    degree: Annotated[Optional[str], Field(description="Degree obtained")]
    linkedin_url: Annotated[str, Field(description="LinkedIn URL of the school")]


class ProfileExperience(BaseModel):
    startsAt: Annotated[datetime, Field(description="Start date of experience")]
    endsAt: Annotated[Optional[datetime], Field(description="End date of experience")]
    company: Annotated[str, Field(description="Company name")]
    description: Annotated[Optional[str], Field(description="Experience description")]
    title: Annotated[Optional[str], Field(description="Job title")]
    location: Annotated[Optional[str], Field(description="Job location")]
    linkedin_url: Annotated[str, Field(description="LinkedIn URL of the company")]


class ProfileVolunteering(BaseModel):
    startsAt: Annotated[datetime, Field(description="Start date of volunteering")]
    endsAt: Annotated[Optional[datetime], Field(description="End date of volunteering")]
    title: Annotated[Optional[str], Field(description="Volunteering title")]
    description: Annotated[Optional[str], Field(description="Volunteering description")]
    location: Annotated[Optional[str], Field(description="Volunteering location")]


class ProfileHonor(BaseModel):
    title: Annotated[Optional[str], Field(description="Honor title")]
    description: Annotated[Optional[str], Field(description="Honor description")]
    issuer: Annotated[Optional[str], Field(description="Honor issuer")]
    issueAt: Annotated[Optional[datetime], Field(description="Date of honor issuance")]


class ProfileProject(BaseModel):
    title: Annotated[Optional[str], Field(description="Project title")]
    description: Annotated[Optional[str], Field(description="Project description")]
    endsAt: Annotated[Optional[datetime], Field(description="Project end date")]
    startsAt: Annotated[Optional[datetime], Field(description="Project start date")]


class ProfileCertification(BaseModel):
    title: Annotated[Optional[str], Field(description="Certification title")]
    description: Annotated[
        Optional[str], Field(description="Certification description")
    ]
    issuer: Annotated[Optional[str], Field(description="Certification issuer")]
    issueAt: Annotated[
        Optional[datetime], Field(description="Date of certification issuance")
    ]


class ProfileLanguage(BaseModel):
    language: Annotated[str, Field(description="Language name")]
    level: Annotated[str, Field(description="Language proficiency level")]


class Profile(BaseModel):
    id: Annotated[str, Field(description="Unique identifier for the profile")]
    country: Annotated[str, Field(description="Country of the profile")]
    city: Annotated[Optional[str], Field(description="City of the profile")]
    state: Annotated[Optional[str], Field(description="State of the profile")]
    headline: Annotated[Optional[str], Field(description="Headline of the profile")]
    summary: Annotated[Optional[str], Field(description="Summary of the profile")]
    connectionCount: Annotated[
        Optional[int], Field(description="Number of connections")
    ]
    followersCount: Annotated[Optional[int], Field(description="Number of followers")]
    isCreator: Annotated[Optional[bool], Field(description="Is the profile a creator")]
    isHiring: Annotated[Optional[bool], Field(description="Is the profile hiring")]
    isOpenToWork: Annotated[
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
