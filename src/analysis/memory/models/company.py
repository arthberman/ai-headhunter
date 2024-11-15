from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


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
    """Information about a specific role within a company.

    Store general patterns and context about what the role typically involves,
    not specific project details. Focus on the essence of the role.

    Example: For a "Software Engineer" role, store "Works on backend systems using Python"
    rather than "Developed feature X for product Y in team Z"
    """

    title: str = Field(description="The standardized job title")
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
    roles: List[Role] = Field(description="List of roles")

    @model_validator(mode="after")
    def check_duplicate_roles(self) -> "CompanyInfo":
        """Check for duplicate role titles and raise error if found."""
        role_titles = {}

        for role in self.roles:
            if role.title in role_titles:
                raise ValueError(
                    f"There are duplicate role titles : must be unique. You should merge information of {role.title} roles."
                )
            role_titles[role.title] = True

        return self
