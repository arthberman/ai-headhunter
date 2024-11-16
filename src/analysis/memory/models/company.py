from typing import Dict, List, Optional

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


class RoleInfo(BaseModel):
    """Information about a specific role within a company.

    Store general patterns and context about what the role typically involves,
    not specific project details. Focus on the essence of the role.

    Example: For a "Software Engineer" role, store "Works on backend systems using Python"
    rather than "Developed feature X for product Y in team Z"
    """

    context: str = Field(
        description="General context about what this role typically involves, including common "
        "responsibilities, focus areas, and working patterns. Should be role-specific "
        "but not tied to individual projects or teams."
        "'meta' details that help understand the essence of the role.",
    )


class CompanyInfo(BaseModel):
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
    softwares: Optional[List[str]] = Field(
        default=None,
        description="Common software tools (e.g., Jira, Zendesk)",
    )
    roles: Dict[str, RoleInfo] = Field(
        default_factory=dict,
        description="Dictionary of roles, where keys are role titles and values are role information",
    )
