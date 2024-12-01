from typing import List, Optional

from pydantic import BaseModel, Field


class LocationInfo(BaseModel):
    """Detailed location information."""

    city: Optional[str] = Field(None, description="City where the job is located")
    region: Optional[str] = Field(
        None, description="State, province, or region where the job is located"
    )
    country: str = Field(description="Country where the job is located (full name)")
    country_code: str = Field(
        description="ISO 3166-1 alpha-2 country code (e.g., 'FR' for France)"
    )


class JobPosting(BaseModel):
    """Structured output of the job posting."""

    title: str = Field(description="Title of the job")
    company: str = Field(description="Name of the company offering the job")
    missions: List[str] = Field(description="List of missions for the job")
    company_spirit: str = Field(
        description="Description of the company spirit (what the company does, why they do it, what they believe in)"
    )
    company_type: Optional[str] = Field(
        None,
        description="Type of company (e.g., fast-growing startup, well-established group)",
    )
    compensation: Optional[str] = Field(
        None, description="Compensation for the job, if specified"
    )
    benefits: Optional[List[str]] = Field(
        None, description="List of benefits for the job, if any"
    )
