from enum import Enum
from typing import List, Optional

from langchain_core.pydantic_v1 import BaseModel, Field


class CompanyStage(str, Enum):
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
    company_stage: CompanyStage = Field(
        ...,
        description="Stage of the company in startup, sme, large corporation or multinational",
    )
    uncertainty: Optional[bool] = Field(
        None,
        description="Flag indicating if there's uncertainty about the accuracy of the information",
    )
