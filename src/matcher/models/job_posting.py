from typing import List, Optional

from langchain_core.pydantic_v1 import BaseModel, Field


class LocationInfo(BaseModel):
    """Detailed location information"""

    city: Optional[str] = Field(description="City where the job is located")
    region: Optional[str] = Field(
        description="State, province, or region where the job is located"
    )
    country: str = Field(description="Country where the job is located (full name)")
    countryCode: str = Field(
        description="ISO 3166-1 alpha-2 country code (e.g., 'FR' for France)"
    )


class JobPosting(BaseModel):
    """Structured output of the job posting"""

    title: str = Field(description="Title of the job")
    company: str = Field(description="Name of the company offering the job")
    department: Optional[str] = Field(
        description="Department or division within the company"
    )

    missions: List[str] = Field(description="List of missions for the job")
    responsibilities: List[str] = Field(
        description="Detailed list of responsibilities for the role"
    )
    hardSkills: List[str] = Field(
        description="List of hard skills required for the job"
    )
    softSkills: List[str] = Field(
        description="List of soft skills required for the job"
    )
    requiredExperience: str = Field(
        description="Type of experience required for the job"
    )
    typicalProfile: str = Field(
        description="Typical profile required for the job (ex: a Data Scientist with +5y of experiences, with a Master Degree in CS)"
    )

    companySpirit: str = Field(
        description="Description of the company spirit (what the company does, why they do it, what they believe in)"
    )

    languages: List[str] = Field(description="List of languages required for the job")
    educationLevel: Optional[str] = Field(
        description="Education level required for the job"
    )

    contractType: str = Field(description="Type of contract for the job")
    location: LocationInfo = Field(
        description="Detailed location information for the job"
    )
    remote: bool = Field(description="Is the job remote")

    compensation: Optional[str] = Field(
        description="Compensation for the job, if specified"
    )
    benefits: Optional[List[str]] = Field(
        description="List of benefits for the job, if any"
    )

    applicationInstructions: Optional[str] = Field(
        description="Instructions for applying to the job"
    )
    careerProgression: Optional[str] = Field(
        description="Information about career progression opportunities"
    )
    diversityStatement: Optional[str] = Field(
        description="Company's statement on diversity and inclusion"
    )

    additionalInformation: Optional[str] = Field(
        description="Any additional important information about the job or company"
    )
