from typing import List, Optional

from pydantic import BaseModel, Field


class LocationInfo(BaseModel):
    """Detailed location information."""

    city: Optional[str] = Field(None, description="City where the job is located")
    region: Optional[str] = Field(
        None, description="State, province, or region where the job is located"
    )
    country: str = Field(description="Country where the job is located (full name)")
    countryCode: str = Field(
        description="ISO 3166-1 alpha-2 country code (e.g., 'FR' for France)"
    )


class JobPosting(BaseModel):
    """Structured output of the job posting."""

    title: str = Field(description="Title of the job")
    company: str = Field(description="Name of the company offering the job")
    department: Optional[str] = Field(
        None, description="Department or division within the company"
    )

    missions: List[str] = Field(description="List of missions for the job")
    responsibilities: List[str] = Field(
        description="Detailed list of responsibilities for the role"
    )
    typicalProfile: str = Field(
        description="Typical profile required for the job (ex: a Data Scientist with +5y of experiences, with a Master Degree in CS)"
    )
    companySpirit: str = Field(
        description="Description of the company spirit (what the company does, why they do it, what they believe in)"
    )
    companyType: Optional[str] = Field(
        None,
        description="Type of company (e.g., fast-growing startup, well-established group)",
    )
    contractType: str = Field(description="Type of contract for the job")
    location: LocationInfo = Field(
        description="Detailed location information for the job"
    )
    remote_policy: str = Field(description="Remote policy for the job")
    compensation: Optional[str] = Field(
        None, description="Compensation for the job, if specified"
    )
    benefits: Optional[List[str]] = Field(
        None, description="List of benefits for the job, if any"
    )
    applicationInstructions: Optional[str] = Field(
        None, description="Instructions for applying to the job"
    )
    careerProgression: Optional[str] = Field(
        None, description="Information about career progression opportunities"
    )
    diversityStatement: Optional[str] = Field(
        None, description="Company's statement on diversity and inclusion"
    )
    additionalInformation: Optional[str] = Field(
        None,
        description="Any additional important information about the job or company",
    )
