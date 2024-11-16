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


class Position(BaseModel):
    """Information about a specific position within a company.

    Store general patterns and context about what the position typically involves,
    not specific project details. Focus on the essence of the role.

    Example: For a "Software Engineer" role, store "Works on backend systems using NestJS and Prisma"
    rather than "Developed feature X during Y quarter in team Z which increased Z by X%"
    """

    title: str = Field(description="The standardized job title")
    description: str = Field(
        description="General context about what this position typically involves, including common "
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
    positions: List[Position] = Field(
        description="List of unique positions. Each position should have a title and context. Position titles must be unique, duplicates are not allowed."
    )

    @model_validator(mode="after")
    def check_duplicate_positions(self) -> "CompanyInfo":
        """Check for duplicate position titles and raise error if found."""
        position_titles = {}

        for position in self.positions:
            if position.title in position_titles:
                raise ValueError(
                    f"There are duplicate position titles : it must be unique. You should merge information of '{position.title}' positions by updating the context of the existing position and removing the duplicate (if any)."
                )
            position_titles[position.title] = True

        return self
