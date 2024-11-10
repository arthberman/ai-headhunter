from typing import List, Optional

from pydantic import BaseModel, Field


class Technologies(BaseModel):
    """Information about the technical stack of a company."""

    cloud_platforms: Optional[List[str]] = Field(
        default=None, description="Cloud platforms used (e.g. AWS, Azure, GCP, etc.)"
    )
    programming_languages: Optional[List[str]] = Field(
        default=None, description="Programming languages used (e.g. Python, Java, etc.)"
    )
    frameworks: Optional[List[str]] = Field(
        default=None,
        description="Frameworks and libraries used (e.g. Django, React, etc.)",
    )


class Role(BaseModel):
    """Information about a specific role within a company."""

    title: str = Field(description="The job title")
    responsibilities: List[str] = Field(description="Key responsibilities of this role")
    softwares: Optional[List[str]] = Field(
        default=None,
        description="Software tools used in this role (e.g., Jira, Zendesk)",
    )


class Company(BaseModel):
    """Information about a company."""

    name: str = Field(description="The official name of the company")
    description: Optional[str] = Field(
        default=None, description="A brief description of the company"
    )
    size: str = Field(
        description="Approximate size range of employees (e.g., 'SME', '1-10', '11-50', '51-200', '201-500', '501+')"
    )
    sector: List[str] = Field(
        description="List of industry sectors the company operates in"
    )
    customer: Optional[List[str]] = Field(
        default=None, description="Types of customers (e.g. B2B, B2C, B2G, C2C, D2C)"
    )
    technologies: Technologies = Field(description="Technical stack information")
    roles: List[Role] = Field(description="List of roles")
