from enum import Enum
from typing import List, Union

from pydantic import BaseModel, Field


class CompanyStage(str, Enum):
    """Stage of the company in startup, sme, large corporation or multinational."""

    STARTUP = "startup"
    SME = "sme"
    LARGE_CORPORATION = "large corporation"
    MULTINATIONAL = "multinational"


class CompanyInfo(BaseModel):
    """Information about a company."""

    linkedin_url: str = Field(..., description="LinkedIn URL of the company")
    name: str = Field(..., description="The name of the company")
    description: str = Field(..., description="A brief description of the company")
    sectors: List[str] = Field(
        ..., description="List of sectors the company operates in"
    )
    company_stage: Union[CompanyStage, None] = Field(
        ...,
        description="Stage of the company in startup, sme, large corporation or multinational",
    )
