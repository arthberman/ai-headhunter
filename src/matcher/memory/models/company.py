from typing import List, Optional

from pydantic import BaseModel, Field


class Role(BaseModel):
    """A role within the company, capturing the actual responsibilities and impact."""

    title: str = Field(
        description="Job title as written in the profile (e.g., 'Sales Manager', 'DevOps Engineer', 'Marketing Director')"
    )

    description: str = Field(
        description="Summary extracted from profile descriptions about what the person does in this role. "
        "Should capture: key responsibilities, tools used, methodologies, scope of work, and notable achievements. "
        "Examples: "
        "'Led digital marketing campaigns using HubSpot, achieving 40% increase in leads', "
        "'Built Kubernetes infrastructure serving 100+ microservices', "
        "'Managed EMEA sales team of 15 people, focusing on enterprise SaaS solutions'"
    )


class CompanyInfo(BaseModel):
    """Information about a company learned from employee LinkedIn profiles.

    This schema captures the company's working environment, tools,
    and actual responsibilities across all types of roles.
    """

    name: str = Field(description="Company name exactly as it appears on LinkedIn")

    industry: str = Field(
        description="Primary industry or sector (e.g., 'Technology', 'Healthcare', 'Financial Services')"
    )

    size: str = Field(
        description="Company size range (e.g., '1-10', '11-50', '51-200', '201-500', '501+')"
    )

    technologies: List[str] = Field(
        description="All significant tools and platforms used at the company. "
        "Includes both technical (e.g., 'Kubernetes', 'Python') and business tools (e.g., 'Salesforce', 'HubSpot'). "
        "These are extracted from role descriptions across all departments"
    )

    roles: List[Role] = Field(
        description="Roles and their real-world resources, extracted from profile descriptions. "
        "This helps understand what people actually do in different positions. "
        "Each role description should reflect actual work, tools used, and scope of responsibility. "
        "Example: A Marketing Manager might use HubSpot and manage international campaigns, "
        "while a DevOps Engineer works with Kubernetes and handles cloud infrastructure"
    )

    description: Optional[str] = Field(
        default=None,
        description="Brief description of the company's main business activities and focus areas",
    )
